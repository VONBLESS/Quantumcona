import pandas as pd
import os
import numpy as np

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Base data directory
BASE_DIR = "data"


# Function to load data from the specified ticker, year, and month
def load_data(ticker):
    # Construct the path for the ticker
    ticker_path = os.path.join(BASE_DIR, f"{ticker}")

    # Load all parquet files in Year/Month structure
    all_data = []

    for year in os.listdir(ticker_path):
        year_path = os.path.join(ticker_path, year)
        if os.path.isdir(year_path):
            for month in os.listdir(year_path):
                month_path = os.path.join(year_path, month)
                if os.path.isdir(month_path):
                    for file_name in os.listdir(month_path):
                        if file_name.endswith(".parquet"):
                            file_path = os.path.join(month_path, file_name)
                            df = pd.read_parquet(file_path)
                            all_data.append(df)

    # Concatenate all DataFrames
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        # combined_df['Date'] = pd.to_datetime(combined_df.index)  # Ensure Date is in datetime format
        combined_df.set_index('Date', inplace=True)  # Set Date as index
        return combined_df
    else:
        raise ValueError(f"No data found for ticker {ticker}")


# Function to filter data based on expiry date
def filter_data_by_start_expiry(df, start_date, expiry_date):
    # Convert expiry_date to datetime
    expiry_date_dt = pd.to_datetime(expiry_date)
    start_date_dt = pd.to_datetime(start_date)
    filtered_df = df[(df.index>=start_date_dt) & (df.index<=expiry_date_dt)]
    return filtered_df


def apply_strategy(df, strategy):
    if strategy == "Moving Average Crossover":
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['Signal'] = 0
        df.iloc[20:, df.columns.get_loc('Signal')] = np.where(
            df.iloc[20:, df.columns.get_loc('SMA_20')] > df.iloc[20:, df.columns.get_loc('SMA_50')], 1, 0)
        df['Position'] = df['Signal'].diff()
    elif strategy == "RSI":
        # Example implementation of RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
    elif strategy == "Bollinger Bands":
        df['MA'] = df['Close'].rolling(window=20).mean()
        df['Upper_Band'] = df['MA'] + (df['Close'].rolling(window=20).std() * 2)
        df['Lower_Band'] = df['MA'] - (df['Close'].rolling(window=20).std() * 2)

    return df

def resample_data(df, timeframe):
    # Mapping for timeframes
    timeframe_mapping = {
        "1 minute": "1T",
        "5 minutes": "5T",
        "1 hour": "1H",
        "1 day": "1D"
    }

    if timeframe in timeframe_mapping:
        return df.resample(timeframe_mapping[timeframe]).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
    else:
        raise ValueError(f"Invalid timeframe: {timeframe}")


# Prompt the user for input parameters
derivative = input("Choose a derivative (Nifty, BankNifty, FinNifty): ").strip()
start_date = input("Specify the start date (YYYY-MM-DD): ").strip()
expiry_date = input("Specify the expiry date (YYYY-MM-DD): ").strip()
timeframes = input("Enter timeframes (e.g., 1 minute, 5 minutes, 1 hour, 1 day) separated by commas: ").split(',')
strategy = input("Choose a trading strategy (Moving Average Crossover, RSI, Bollinger Bands): ").strip()

# Map the user input to actual ticker symbols
ticker_map = {
    "Nifty": "NSEI",
    "BankNifty": "^NSEBANK",
    "FinNifty": "NIFTY_FIN_SERVICE.NS"
}

# Load and process data based on user inputs
if derivative in ticker_map:
    ticker = ticker_map[derivative]
    df = load_data(ticker)
    # Filter the data based on expiry date if applicable
    if expiry_date and start_date and start_date<expiry_date:
        df = filter_data_by_start_expiry(df, start_date, expiry_date)
        print(df)

    for timeframe in timeframes:
        print(f"Processing data for {timeframe} timeframe...")
        resampled_df = resample_data(df, timeframe)

        if strategy:
            resampled_df = apply_strategy(resampled_df, strategy)
            # Display the processed data
            print(resampled_df)
            output_file = f"task2_{strategy}_trading_signals.xlsx"
            resampled_df.to_excel(output_file, index=True)
