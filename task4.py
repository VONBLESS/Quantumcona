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
    # Apply the strategy function to the resampled data
    df_signals = strategy_func(df_resampled)

    # Calculate trade statistics
    df_signals['Position'] = df_signals['Signal'].diff()

    # Calculate the number of trades
    num_trades = len(df_signals[df_signals['Position'] != 0])
    print("number of trades", num_trades)

    # Total profit/loss calculation using Entry_Price and Exit_Price
    total_profit_loss = (df_signals['Exit_Price'].sum() - df_signals['Entry_Price'].sum())
    print(f"total profit or loss {total_profit_loss}")
    print(df_signals['Exit_Price'], df_signals['Entry_Price'])
    # print("length", len(df_signals[df_signals['Exit_Price'] > df_signals['Entry_Price']]))
    win_rate = (len(df_signals[df_signals['Exit_Price'] > df_signals['Entry_Price']]) / num_trades * 100) if num_trades > 0 else 0

    # Example risk-adjusted metrics
    df_signals['Return'] = (df_signals['Exit_Price'] - df_signals['Entry_Price']) / df_signals['Entry_Price']
    sharpe_ratio = np.mean(df_signals['Return']) / np.std(df_signals['Return']) if np.std(df_signals['Return']) != 0 else 0
    df_signals['Drawdown'] = df_signals['Return'].cumsum() - df_signals['Return'].cumsum().cummax()
    max_drawdown = df_signals['Drawdown'].min() if not df_signals['Drawdown'].empty else 0

    backtest_results = {
        'Timeframe': timeframe,
        'Number of Trades': num_trades,
        'Total Profit/Loss': total_profit_loss,
        'Win Rate (%)': win_rate,
        'Sharpe Ratio': sharpe_ratio,
        'Maximum Drawdown': max_drawdown
    }

    return backtest_results

if __name__ == "__main__":
    derivative = input("Choose a derivative (Nifty, BankNifty, FinNifty): ").strip()
    strategy = input("Choose a strategy (Moving Average Crossover, RSI): ").strip()

    timeframe_list = ["1Min"] #['1Min', '5Min', '1h', '1D', '1ME']  # Define the list of timeframes to backtest
    ticker_map = {
        "Nifty": "NSEI",
        "BankNifty": "^NSEBANK",
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
