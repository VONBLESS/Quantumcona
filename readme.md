All tasks given on task.pdf file in this repo
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

# Task 3

# Derivatives Backtesting with Signal Generation

This project implements a backtesting framework that allows users to load historical data for derivatives (Nifty, BankNifty, FinNifty) and generate trading signals based on selected strategies. The strategies include Moving Average Crossover and RSI, with optional stop-loss functionality. Users can dynamically select the derivative, strategy, and expiry date.

## Key Features
- **Data Loading:** Loads historical data for Nifty, BankNifty, and FinNifty from Parquet files organized in a Year/Month structure.
- **Moving Average Crossover Strategy:** Buy and sell signals based on the crossover of short-term and long-term moving averages.
- **RSI (Relative Strength Index) Strategy:** Buy when oversold (RSI < 30) and sell when overbought (RSI > 70).
- **Stop-Loss Logic:** Optional stop-loss mechanism to manage risk by automatically exiting positions when losses exceed a predefined percentage.
- **Support for Multiple Expiries:** Handles multiple expiries and derivatives with dynamic data loading.

## Directory Structure
The historical data is stored in the `data` folder, structured by Year and Month:


The processed trading signals are saved in the `output` folder:


## Strategies
### 1. **Moving Average Crossover**
This strategy generates buy and sell signals based on the crossover of two moving averages:
- **Buy Signal:** When the short-term moving average (e.g., 20-day) crosses above the long-term moving average (e.g., 50-day).
- **Sell Signal:** When the short-term moving average crosses below the long-term moving average.
- **Stop-Loss:** Automatically exits the trade if the price falls below a certain percentage (default is 8%) from the entry price.

### 2. **RSI (Relative Strength Index)**
This strategy generates buy and sell signals based on the RSI indicator:
- **Buy Signal:** When RSI < 30, indicating oversold conditions.
- **Sell Signal:** When RSI > 70, indicating overbought conditions.
- **Stop-Loss:** Automatically exits the trade if the price drops by more than 2% from the entry price.

## How It Works
1. **Load Historical Data:**
   - The script loads historical data for the selected derivative (`Nifty`, `BankNifty`, `FinNifty`).
   - Data is stored in Parquet format, organized by Year/Month.

2. **Select Trading Strategy:**
   - The user selects one of the following strategies: Moving Average Crossover or RSI.

3. **Generate Trading Signals:**
   - Based on the selected strategy, buy/sell signals are generated.
   - The script includes optional stop-loss logic to manage risk.

4. **Save Results:**
   - The generated signals and relevant data (e.g., entry/exit prices) are saved to an Excel file in the `output` folder.

## Input Parameters
1. **Derivative Selection:** Choose from Nifty, BankNifty, or FinNifty.
2. **Strategy Selection:** Select either Moving Average Crossover or RSI.
3. **Optional Parameters:**
   - **Stop-Loss Percentage**: Define a stop-loss percentage for risk management.
   - **Short-term and Long-term Window:** Customize the short-term and long-term windows for the Moving Average Crossover strategy.
   - **RSI Period:** Customize the period for the RSI calculation.

## Trading Strategies in Detail
### Moving Average Crossover
- **Buy Signal:** When the short-term moving average crosses above the long-term moving average.
- **Sell Signal:** When the short-term moving average crosses below the long-term moving average.
- **Stop-Loss:** Automatically exits the trade if the price falls more than the specified percentage below the entry price.
```
def moving_average_crossover(df, short_window=20, long_window=50, stop_loss_pct=0.08):
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
        elif df['Signal'].iloc[i] == -1 and position == 'long':
            # Exit long position
            position = None
            df.iloc[i, df.columns.get_loc('Exit_Price')] = df['Close'].iloc[i]
        elif position == 'long':
            # Check for stop-loss condition
            if df['Close'].iloc[i] < entry_price * (1 - stop_loss_pct):
                position = None
                df.iloc[i, df.columns.get_loc('Exit_Price')] = df['Close'].iloc[i]
```

### RSI (Relative Strength Index)
- **Buy Signal:** When RSI is below 30 (oversold conditions).
- **Sell Signal:** When RSI is above 70 (overbought conditions).
- **Stop-Loss:** Automatically exits the trade if the price drops more than the specified percentage below the entry price.
```
def rsi_strategy(df, rsi_period=14, rsi_oversold=30, rsi_overbought=70, stop_loss_pct=0.02):
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    df['Signal'] = 0
    df.loc[df['RSI'] < 30, 'Signal'] = 1  # Buy signal
    df.loc[df['RSI'] > 70, 'Signal'] = -1  # Sell signal

    # Stop-loss implementation
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
        elif df['Signal'].iloc[i] == -1 and position == 'long':
            # Exit long position
            position = None
            df.iloc[i, df.columns.get_loc('Exit_Price')] = df['Close'].iloc[i]
        elif position == 'long':
            # Check for stop-loss condition
            if df['Close'].iloc[i] < entry_price * (1 - stop_loss_pct):
                position = None
                df.iloc[i, df.columns.get_loc('Exit_Price')] = df['Close'].iloc[i]
```

# Task 4

# Backtesting Trading Strategies Across Timeframes

This project implements a backtesting framework for trading strategies on financial derivatives (Nifty, BankNifty, FinNifty). It allows users to apply and evaluate strategies such as Moving Average Crossover and RSI across multiple timeframes.

## Overview

The backtesting framework:
- Loads historical market data.
- Applies selected trading strategies.
- Resamples data for different timeframes (1 minute, 5 minutes, 1 hour, daily).
- Generates performance metrics for each strategy and timeframe.
- ```
  def backtest_strategy(df, strategy_func, timeframe):
    df_resampled = df.resample(timeframe).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()
    df_signals = strategy_func(df_resampled)
    df_signals['Position'] = df_signals['Signal'].diff()

    df_signals['Returns'] = df_signals['Close'].pct_change()
    df_signals['Strategy_Returns'] = df_signals['Returns'] * df_signals['Position'].shift(1)

    # Calculate backtesting metrics
    num_trades = len(df_signals['Position'][df_signals['Position'] != 0])
    total_profit_loss = df_signals['Strategy_Returns'].sum()
    win_rate = (df_signals['Strategy_Returns'][df_signals['Strategy_Returns'] > 0].count() / num_trades) * 100
    sharpe_ratio = df_signals['Strategy_Returns'].mean() / df_signals['Strategy_Returns'].std()
    max_drawdown = (df_signals['Strategy_Returns'].cumsum().max() - df_signals['Strategy_Returns'].cumsum().min()) / df_signals[
        'Strategy_Returns'].cumsum().max()

    results = {
        'Number of Trades': num_trades,
        'Total Profit/Loss': total_profit_loss,
        'Win Rate': win_rate,
        'Sharpe Ratio': sharpe_ratio,
        'Maximum Drawdown': max_drawdown
    }

    return results
  ```

## Key Features
- **Multiple Timeframe Backtesting:** Evaluate strategies across various timeframes, including 1 minute, 5 minutes, 1 hour, and daily.
- **Performance Metrics:** Provides insights into trading performance, including:
  - Number of trades
  - Total profit/loss
  - Win rate (percentage of profitable trades)
  - Sharpe ratio (risk-adjusted return)
  - Maximum drawdown (largest drop from a peak)

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/VONBLESS/historical-data-management.git
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
