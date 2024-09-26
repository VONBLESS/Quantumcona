import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# Parallel processing with Dask (if dataset grows very large)
import dask.dataframe as dd

tickers = ['^NSEI', '^NSEBANK', 'NIFTY_FIN_SERVICE.NS']

# Data over 5 year period
start_date = '2018-01-01'
end_date = datetime.now().strftime('%Y-%m-%d')

# Directory to store partitioned data
DATA_DIR = 'data/'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


# Download historical data from Yahoo Finance
def fetch_data(ticker):
    print(f"Fetching data for {ticker}")
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            print(f"No data found for {ticker}")
            return None
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


# Save the data to partitioned Parquet files (partitioning by Year/Month to reduce number of partitions)
def save_to_parquet(df, file_name):
    print(f"Saving {file_name} partitioned by Year and Month")

    # Ensure the index is in Datetime format
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)

    # Extract Year and Month for partitioning
    df['Year'] = df.index.year
    df['Month'] = df.index.month
    df.reset_index(inplace=True)

    # Save the data, partitioned by Year and Month for efficient querying
    df.to_parquet(f"{DATA_DIR}{file_name}", partition_cols=['Year', 'Month'])


# Loading data efficiently
def load_data(file_name):
    print(f"Loading {file_name} using Dask for efficient processing")
    # Use Dask for large datasets
    df = dd.read_parquet(f"{DATA_DIR}{file_name}")
    return df


# Process and save all ticker data
def process_and_save_all_data(tickers):
    for ticker in tickers:
        df = fetch_data(ticker)
        if df is not None:
            save_to_parquet(df, ticker.replace('^', '').replace('.', '_'))


# Download and partition the data
process_and_save_all_data(tickers)

# Example of loading Nifty data for processing
nifty_df = load_data('^NSEI'.replace('^', '').replace('.', '_'))
print(nifty_df.head())
nifty_df = load_data('NSEBANK')
print(nifty_df.head())

# Placeholder function for filtering by expiry dates (options or futures)
def filter_by_expiry(data, expiry_date):
    # Assuming data has an 'expiry' column (replace with real options/futures data)
    filtered_data = data[data['expiry'] == expiry_date]
    return filtered_data

# Example call (when you have actual options data)
# expiry_date = '2023-12-28'
# filtered_options = filter_by_expiry(nifty_options_data, expiry_date)
