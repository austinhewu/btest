import pandas as pd


def sma(df, window=147):
    """Return a simple moving average from a specified window in the 'close' column of DataFrame df."""
    return df['close'].rolling(window=window, min_periods=1).mean()


def trade1(df):
    df['position'] = 0  # long -> +1, short -> -1,
    df['trade_price'] = 0
    df['P/L'] = 0
    df['%P/L'] = 0
    df['total_P/L'] = 0
    entry = 0
    first_entry = False

    for i in range(1, len(df['close'])):
        if df.loc[i, 'close'] > df.loc[i, 'SMA'] and df.loc[i - 1, 'close'] <= df.loc[i - 1, 'SMA']:
            # close up cross SMA
            df.loc[i, 'position'] = 1
            df.loc[i, 'trade_price'] = df.loc[i, 'close']
            entry = df.loc[i, 'close']
            first_entry = True
        elif df.loc[i, 'close'] < df.loc[i, 'SMA'] and df.loc[i - 1, 'close'] >= df.loc[i - 1, 'SMA'] and first_entry:
            # close down cross SMA
            df.loc[i, 'position'] = 0
            df.loc[i, 'trade_price'] = df.loc[i, 'close']
            if df.loc[i - 1, 'position'] == 1:  # if previously long, calculate P/L and %P/L
                df.loc[i, 'P/L'] = df.loc[i, 'close'] - entry
                if entry != 0:
                    df.loc[i, '%P/L'] = (df.loc[i, 'P/L'] / entry) * 100
        else:  # hold position
            df.loc[i, 'position'] = df.loc[i - 1, 'position']
            if df.loc[i, 'position'] == 1:  # if holding investment, calculate P/L and %P/L
                df.loc[i, 'P/L'] = df.loc[i, 'close'] - entry
                if entry != 0:
                    df.loc[i, '%P/L'] = (df.loc[i, 'P/L'] / entry) * 100

    for i in range(1, len(df['close'])):  # total P/L counter
        df.loc[i, 'total_P/L'] = df.loc[i - 1, 'total_P/L'] + df.loc[i, 'P/L']

    return df


data_path = 'C:/Users/Austin/Downloads/BTEST/BTEST clean - [1].csv'
data = pd.read_csv(data_path, parse_dates=['time'])
data = data.sort_values(by='time')
data['SMA'] = sma(data)
data = trade1(data)
output_path = 'C:/Users/Austin/Downloads/BTEST/BTEST output 1.csv'
data.to_csv(output_path, index=False)
