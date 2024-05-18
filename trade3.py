import pandas as pd


def sma(df, window=147):
    """Return a simple moving average from a specified window in the 'close' column of DataFrame df."""
    return df['close'].rolling(window=window, min_periods=1).mean()


def bollinger_bands(df, window=147, num_std_devs=2):
    """Return bollinger bands over a specified window with a given number of standard deviations."""
    rolling_avg = df['close'].rolling(window=window, min_periods=1).mean()
    std_dev = df['close'].rolling(window=window, min_periods=1).std()
    df['lower_band'] = rolling_avg - (std_dev * num_std_devs)
    df['upper_band'] = rolling_avg + (std_dev * num_std_devs)
    return df


def trade3(df):
    df['position'] = 0  # long -> +1, short -> -1, max = 2
    df['trade_price_1'] = 0
    df['trade_price_2'] = 0
    df['P/L'] = 0
    df['%P/L'] = 0
    df['total_P/L'] = 0
    entry_1 = 0
    entry_2 = 0
    pause = False
    sl_index = False

    for i in range(1, len(df['close'])):
        if df.loc[i - 1, 'position'] == 1:  # update P/L for ongoing position
            df.loc[i, 'P/L'] = df.loc[i, 'close'] - entry_1
            df.loc[i, '%P/L'] = (df.loc[i, 'P/L'] / entry_1) * 100
        elif df.loc[i - 1, 'position'] == 2:
            df.loc[i, 'P/L'] = df.loc[i, 'close'] * 2 - entry_1 - entry_2
            if entry_1 != 0 and entry_2 != 0:
                df.loc[i, '%P/L'] = (df.loc[i, 'P/L'] / (entry_1 + entry_2)) * 100

        if df.loc[i, '%P/L'] < -1 and df.loc[i - 1, 'position'] > 0:  # stop-loss for %P/L < -1
            df.loc[i, 'position'] = df.loc[i - 1, 'position'] - 1
            sl_index = True
            pause = True
        if pause:
            if df.loc[i, 'high'] > df.loc[i, 'upper_band'] and df.loc[i - 1, 'high'] <= df.loc[i - 1, 'upper_band']:
                # paused + high up cross upper band -> unpause
                df.loc[i, 'position'] = df.loc[i - 1, 'position']
                pause = False
            elif not sl_index:  # hold position
                df.loc[i, 'position'] = df.loc[i - 1, 'position']
            sl_index = False
        else:
            if df.loc[i, 'high'] > df.loc[i, 'upper_band'] and df.loc[i - 1, 'high'] <= df.loc[i - 1, 'upper_band']:
                # high up cross upper band -> sell signal
                if df.loc[i - 1, 'position'] > 0:
                    df.loc[i, 'position'] = df.loc[i - 1, 'position'] - 1
            elif df.loc[i, 'low'] < df.loc[i, 'lower_band'] and df.loc[i - 1, 'low'] >= df.loc[i - 1, 'lower_band']:
                # low down cross lower band -> buy signal
                if df.loc[i - 1, 'position'] == 0:
                    df.loc[i, 'position'] = df.loc[i - 1, 'position'] + 1
                    entry_1 = df.loc[i, 'close']
                    df.loc[i, 'trade_price_1'] = df.loc[i, 'close']
                elif df.loc[i - 1, 'position'] == 1:
                    df.loc[i, 'position'] = df.loc[i - 1, 'position'] + 1
                    entry_2 = df.loc[i, 'close']
                    df.loc[i, 'trade_price_2'] = df.loc[i, 'close']
            else:  # hold position
                df.loc[i, 'position'] = df.loc[i - 1, 'position']

    for i in range(1, len(df['close'])):  # total P/L counter
        df.loc[i, 'total_P/L'] = df.loc[i - 1, 'total_P/L'] + df.loc[i, 'P/L']

    return df


data_path = 'C:/Users/Austin/Downloads/BTEST/BTEST clean - [1].csv'
data = pd.read_csv(data_path, parse_dates=['time'])
data = data.sort_values(by='time')
data['SMA'] = sma(data)
data = bollinger_bands(data)
data = trade3(data)
output_path = 'C:/Users/Austin/Downloads/BTEST/BTEST output 3.csv'
data.to_csv(output_path, index=False)
