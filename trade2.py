import pandas as pd


def sma(df, window=147):
    """Return a simple moving average from a specified window in the 'close' column of DataFrame df."""
    return df['close'].rolling(window=window, min_periods=1).mean()


def trade2(df):
    df['position'] = 0  # long -> +1, short -> -1
    df['trade_price'] = 0
    df['P/L'] = 0
    df['%P/L'] = 0
    df['total_P/L'] = 0
    entry = 0
    first_entry = False
    stop_loss = False

    for i in range(1, len(df['close'])):
        if df.loc[i - 1, 'position'] == 1 and first_entry:  # update P/L and %P/L for ongoing position
            df.loc[i, 'P/L'] = df.loc[i, 'close'] - entry
            if entry != 0:
                df.loc[i, '%P/L'] = (df.loc[i, 'P/L'] / entry) * 100
        if df.loc[i, '%P/L'] < -1 and df.loc[i - 1, 'position'] == 1:  # stop-loss for %P/L < -1
            df.loc[i, 'position'] = 0
            df.loc[i, 'trade_price'] = df.loc[i, 'close']
            df.loc[i, 'P/L'] = df.loc[i, 'close'] - entry
            if entry != 0:
                df.loc[i, '%P/L'] = (df.loc[i, 'P/L'] / entry) * 100
            stop_loss = True
        elif df.loc[i, 'close'] > df.loc[i, 'SMA'] and df.loc[i - 1, 'close'] <= df.loc[i - 1, 'SMA']:
            # close up cross SMA -> buy signal
            df.loc[i, 'position'] = 1
            df.loc[i, 'trade_price'] = df.loc[i, 'close']
            entry = df.loc[i, 'close']
            first_entry = True
            stop_loss = False
        elif (df.loc[i, 'close'] < df.loc[i, 'SMA'] and df.loc[i - 1, 'close'] >= df.loc[i - 1, 'SMA'] and first_entry
              and not stop_loss):
            # close down cross SMA -> sell signal
            df.loc[i, 'position'] = 0
            df.loc[i, 'trade_price'] = df.loc[i, 'close']
            if df.loc[i - 1, 'position'] == 1:  # if previously long, calculate P/L and %P/L
                df.loc[i, 'P/L'] = df.loc[i, 'close'] - entry
                if entry != 0:
                    df.loc[i, '%P/L'] = (df.loc[i, 'P/L'] / entry) * 100
        else:  # hold position
            df.loc[i, 'position'] = df.loc[i - 1, 'position']

    for i in range(1, len(df['close'])):  # total P/L counter
        df.loc[i, 'total_P/L'] = df.loc[i - 1, 'total_P/L'] + df.loc[i, 'P/L']

    return df


data_path = 'C:/Users/Austin/Downloads/BTEST/BTEST clean - [1].csv'
data = pd.read_csv(data_path, parse_dates=['time'])
data = data.sort_values(by='time')
data['SMA'] = sma(data)
data = trade2(data)
output_path = 'C:/Users/Austin/Downloads/BTEST/BTEST output 2.csv'
data.to_csv(output_path, index=False)
