Here’s a sample `README.md` for your GitHub repository based on your task and code:

---
# Task 1
## Historical Data Management for Derivatives

This project provides an efficient solution for managing large historical datasets of derivatives such as Nifty, BankNifty, FinNifty, and BankEx, including multiple option expiries. The project handles data extraction, processing, and filtering based on expiry dates using Yahoo Finance and other sources like ICICI Breeze API or data extracted from Telegram channels.

## Key Features
- **Efficient Data Loading:** Uses Dask for parallel processing of large datasets.
- **Data Partitioning:** Saves data partitioned by Year and Month using the Parquet format for efficient querying and storage.
- **Expiry-Based Filtering:** Provides a function to filter derivative data based on options expiry.
- **Support for Multiple Derivatives:** Handles data for multiple indices (Nifty, BankNifty, FinNifty) simultaneously.

## Data Source
The data is fetched using:
1. **Yahoo Finance:** For historical data of Nifty, BankNifty, and FinNifty.
2. **Alternative Sources (Optional):** 
   - **Telegram Channel:** Historical data files may be extracted from `.feather` and `.zip` formats available on the channel [here](https://2ly.link/1ztTU).
   - **ICICI Breeze API:** For accessing historical options and futures data.

## Technologies Used
- **Pandas:** For data manipulation.
- **Dask:** For handling large datasets with parallel processing.
- **Yahoo Finance API (yfinance):** To download historical data.
- **Parquet:** For efficient data storage and partitioning.
- **Feather:** For working with Feather files (optional, if data is extracted from Telegram or other sources).
  
## Data Storage and Retrieval Strategy
### Data Structure:
1. **Partitioning by Year and Month:** 
   - Data is stored in the Parquet format in subdirectories organized by Year and Month. This reduces the number of partitions and allows for efficient querying and access.
   - Example structure:
     ```
     data/
        ^NSEI/
            Year=2020/
                Month=1/
                    part-0000.parquet
                Month=2/
                    part-0000.parquet
            Year=2021/
                Month=1/
                    part-0000.parquet
     ```

2. **Multiple Derivatives Support:** 
   - Data for multiple tickers (`^NSEI`, `^NSEBANK`, `NIFTY_FIN_SERVICE.NS`) is handled separately, ensuring modular and clean data handling.

### Expiry-Based Filtering:
- Data is filtered dynamically based on expiry dates for options contracts. Once the data is loaded, expiry-based strategies can be applied using the `filter_by_expiry` function, assuming the dataset includes expiry information.

### Storage Format:
- **Parquet:** Highly efficient for large datasets, supports partitioning, and is compatible with Dask for distributed data processing.
- **Feather:** Optional, if historical data is sourced from `.feather` files (from Telegram).

## Code Overview
### 1. Fetch Historical Data
```python
def fetch_data(ticker):
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    return data
```
Fetches historical data from Yahoo Finance for a given ticker.

### 2. Save Data to Partitioned Parquet
```python
def save_to_parquet(df, file_name):
    df.to_parquet(f"{DATA_DIR}{file_name}", partition_cols=['Year', 'Month'])
```
Saves the data into partitioned Parquet files, organized by Year and Month.

### 3. Load Data Efficiently with Dask
```python
def load_data(file_name):
    df = dd.read_parquet(f"{DATA_DIR}{file_name}")
    return df
```
Loads large datasets using Dask for parallel processing.

### 4. Filter Data by Expiry (Options)
```python
def filter_by_expiry(data, expiry_date):
    filtered_data = data[data['expiry'] == expiry_date]
    return filtered_data
```
Filters the loaded data based on the expiry date for options contracts.

## Usage
### 1. Download and Save Historical Data
Run the script to download and save historical data:
```bash
python task1.py
```

### 2. Load and Filter Data by Expiry
```python
nifty_df = load_data('NSEI')
filtered_options = filter_by_expiry(nifty_df, '2023-12-28')
```


# Task 2
# Derivatives Backtesting with User Input Parameters

This project allows users to load and analyze historical data for different derivatives such as Nifty, BankNifty, and FinNifty. The script lets the user choose various input parameters like timeframes, expiry dates, and trading strategies, then processes the data accordingly.

## Key Features
- **User Input Parameters:** Users can input parameters such as derivative type, expiry date, and timeframes to filter and process data.
- **Data Resampling:** The script resamples the historical data based on the user's selected timeframe (e.g., 1 minute, 5 minutes, 1 hour, 1 day).
- **Trading Strategies:** Users can choose from several pre-built trading strategies such as Moving Average Crossover, RSI, and Bollinger Bands.
- **Data Filtering by Expiry Date:** Users can specify an expiry date to filter the dataset for options or futures contracts.

## Input Parameters
1. **Derivative Type:** Choose a derivative like Nifty, BankNifty, or FinNifty to load historical data.
2. **Expiry Date (Optional):** Specify an expiry date to filter options or futures data based on the contract's expiry.
3. **Timeframes:** Select multiple timeframes for backtesting. Available options include:
   - 1 minute
   - 5 minutes
   - 1 hour
   - 1 day
   - ```
     def resample_data(df, timeframe):
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
     ```
4. **Trading Strategy:** Choose from the following strategies:
   - **Moving Average Crossover:** Generates buy/sell signals based on the crossover of short-term and long-term moving averages (e.g., 20-day SMA vs. 50-day SMA).
   - ```
      if strategy == "Moving Average Crossover":
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['Signal'] = 0
        df.iloc[20:, df.columns.get_loc('Signal')] = np.where(
            df.iloc[20:, df.columns.get_loc('SMA_20')] > df.iloc[20:, df.columns.get_loc('SMA_50')], 1, 0)
        df['Position'] = df['Signal'].diff()
   
     ```
   - **RSI (Relative Strength Index):** Uses the RSI to detect overbought or oversold conditions.
   - ```
      elif strategy == "RSI":
        # Example implementation of RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
     ```
   - **Bollinger Bands:** Identifies potential buy/sell signals based on the upper and lower Bollinger Bands.
   - ```
      elif strategy == "Bollinger Bands":
        df['MA'] = df['Close'].rolling(window=20).mean()
        df['Upper_Band'] = df['MA'] + (df['Close'].rolling(window=20).std() * 2)
        df['Lower_Band'] = df['MA'] - (df['Close'].rolling(window=20).std() * 2)
     ```

## How It Works
1. **Load Historical Data:**
   - The script loads historical data stored in Parquet format. The data is organized by Year and Month directories.
   - Example structure:
     ```
     data/
        NSEI/
            Year=2020/
                Month=1/
                    part-0000.parquet
                Month=2/
                    part-0000.parquet
     ```
2. **Filter Data by Expiry Date (Optional):**
   - If the user specifies an expiry date, the script filters the data to only include records from the start date to the expiry date.
3. **Resample Data Based on Timeframes:**
   - The data is resampled based on the selected timeframe (e.g., 1 minute, 1 hour) to aggregate the data for analysis.
4. **Apply Trading Strategy:**
   - The selected trading strategy (Moving Average Crossover, RSI, Bollinger Bands) is applied to the resampled data to generate trading signals.
5. **Export Processed Data:**
   - The final processed data, including trading signals, is saved as an Excel file in the `output` directory.
  

     

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/VONBLESS/historical-data-management.git
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
