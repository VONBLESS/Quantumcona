import pandas as pd
import numpy as np
from task3 import load_data, moving_average_crossover, rsi_strategy

def backtest_strategy(df, strategy_func, timeframe):

    # Resample data based on the timeframe
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


if __name__ == "__main__":
    derivative = input("Choose a derivative (Nifty, BankNifty, FinNifty): ").strip()
    strategy = input("Choose a strategy (Moving Average Crossover, RSI): ").strip()

    timeframe_list = ['1Min', '5Min', '1h', '1D', '1ME']  # Define the list of timeframes to backtest
    ticker_map = {
        "Nifty": "NSEI",
        "BankNifty": "NSEBANK",
        "FinNifty": "NIFTY_FIN_SERVICE.NS"
    }

    if derivative in ticker_map and strategy in ['Moving Average Crossover', 'RSI']:
        ticker = ticker_map[derivative]
        df = load_data(ticker)

        if strategy == "Moving Average Crossover":
            strategy_func = moving_average_crossover
        elif strategy == "RSI":
            strategy_func = rsi_strategy

        results = []
        for timeframe in timeframe_list:
            print(f"Backtesting {strategy} strategy on {derivative} for {timeframe} timeframe...")
            backtest_result = backtest_strategy(df, strategy_func, timeframe)
            results.append(backtest_result)
            print("Backtest Results:")
            for key, value in backtest_result.items():
                print(f"{key}: {value}")
            print("-" * 30)

        # Optionally, you can save or further process the results here
    else:
        print("Invalid derivative or strategy selected.")
