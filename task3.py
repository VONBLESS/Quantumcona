import numpy as np
import pandas as pd
import os

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

BASE_DIR = "data"

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

# Strategy: Moving Average Crossover
def moving_average_crossover(df, short_window=20, long_window=50, stop_loss_pct=0.08):
    """
    Moving Average Crossover strategy with stop-loss logic.

    Buy when short-term MA crosses above long-term MA.
    Sell when short-term MA crosses below long-term MA.

    Stop-loss: Exits trade if price falls by stop_loss_pct from the entry price.
    """
    df['SMA_Short'] = df['Close'].rolling(window=short_window).mean()
    df['SMA_Long'] = df['Close'].rolling(window=long_window).mean()

    df['Signal'] = 0
    df['Signal'] = np.where(df['SMA_Short'] > df['SMA_Long'], 1, -1)


    # Stop-loss implementation
    df['Entry_Price'] = np.nan
    df['Exit_Price'] = np.nan
    position = None
    entry_price = None

    for i in range(1, len(df)):
        if df['Signal'].iloc[i] == 1 and position != 'long':
            # Enter buy (long) position
            position = 'long'
            entry_price = df['Close'].iloc[i]
            df.iloc[i, df.columns.get_loc('Entry_Price')] = entry_price
            # print(f"Entry Price set at index {i}: {entry_price}")
        elif df['Signal'].iloc[i] == -1 and position == 'long':
            # Exit long position
            position = None
            df.iloc[i, df.columns.get_loc('Exit_Price')] = df['Close'].iloc[i]
            # print(f"Exit Price set at index {i}: {df['Close'].iloc[i]}")
        elif position == 'long':
            # Check for stop-loss condition
            if df['Close'].iloc[i] < entry_price * (1 - stop_loss_pct):
                position = None
                df.iloc[i, df.columns.get_loc('Exit_Price')] = df['Close'].iloc[i]
                # print(f"Exit Price set at index {i}: {df['Close'].iloc[i]}")


    return df


# Strategy: RSI (Relative Strength Index)
def rsi_strategy(df, rsi_period=14, rsi_oversold=30, rsi_overbought=70, stop_loss_pct=0.02):
    """
    RSI strategy with stop-loss logic.

    Buy when RSI < 30 (oversold).
    Sell when RSI > 70 (overbought).

    Stop-loss: Exits trade if price falls by stop_loss_pct from the entry price.
    """
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    df['Signal'] = 0
    df.loc[df['RSI'] < 30, 'Signal'] = 1  # Buy signal
    df.loc[df['RSI'] > 70, 'Signal'] = -1  # Sell signal

    # Stop-loss implementation
    # df['Entry_Price'] = np.nan
    # df['Exit_Price'] = np.nan
    df['Entry_Price'] = np.where(df['Signal'] == 1, df['Close'], np.nan)
    df['Exit_Price'] = np.where(df['Signal'] == -1, df['Close'], np.nan)

    position = None
    entry_price = None

    for i in range(1, len(df)):
        if df['Signal'].iloc[i] == 1 and position != 'long':
            # Enter buy (long) position
            position = 'long'
            entry_price = df['Close'].iloc[i]
            df.iloc[i, df.columns.get_loc('Entry_Price')] = entry_price
            # print(f"Entry Price set at index {i}: {entry_price}")
        elif df['Signal'].iloc[i] == -1 and position == 'long':
            # Exit long position
            position = None
            df.iloc[i, df.columns.get_loc('Exit_Price')] = df['Close'].iloc[i]
            # print(f"Exit Price set at index {i}: {df['Close'].iloc[i]}")
        elif position == 'long':
            # Check for stop-loss condition
            if df['Close'].iloc[i] < entry_price * (1 - stop_loss_pct):
                position = None
                df.iloc[i, df.columns.get_loc('Exit_Price')] = df['Close'].iloc[i]
                # print(f"Exit Price set at index {i}: {df['Close'].iloc[i]}")

    return df

if __name__ == "__main__":

    ticker_map = {
        "Nifty": "NSEI",
        "BankNifty": "^NSEBANK",
        "FinNifty": "NIFTY_FIN_SERVICE.NS"
    }

    derivative = input("Choose a derivative (Nifty, BankNifty, FinNifty): ").strip()

    # Load and process data based on user inputs
    if derivative in ticker_map:
        ticker = ticker_map[derivative]
        df = load_data(ticker)
        strategy = input("Choose a strategy (Moving Average Crossover, RSI): ").strip()

        if strategy == "Moving Average Crossover":
            df = moving_average_crossover(df)
            output_file = "MAC_trading_signals.xlsx"
            df.to_excel(output_file, index=True)
            # print(df[['Close', 'SMA_Short', 'SMA_Long', 'Signal', 'Entry_Price', 'Exit_Price']])
        elif strategy == "RSI":
            df = rsi_strategy(df)
            output_file = "RSI_trading_signals.xlsx"
            df.to_excel(output_file, index=True)
            # print(df[['Close', 'RSI', 'Signal', 'Entry_Price', 'Exit_Price']])
        else:
            print("Invalid strategy selected.")

