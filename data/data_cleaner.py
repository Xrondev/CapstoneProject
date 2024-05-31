import numpy as np
import pandas as pd
import glob

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


def build_price_data(lookback_window=168):
    def load_data_with_stock_name(file):
        df = pd.read_csv(file)
        stock_name = file.split('/')[-1].split('_')[1]  # Extract stock name from the file name
        df['Stock'] = stock_name
        return df

    # Load all CSV files into a single DataFrame
    price_files = glob.glob('./csv_eodhd/price/*.csv')
    price_dfs = [load_data_with_stock_name(file) for file in price_files]
    price_data = pd.concat(price_dfs, ignore_index=True)

    price_data.set_index('Timestamp', inplace=True)
    price_data.fillna(method='ffill', inplace=True)

    def add_technical_indicators(df):
        df['MA_10'] = df['Close'].rolling(window=10).mean()
        df['MA_50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = compute_rsi(df['Close'])
        df['MACD'], df['MACD_signal'], df['MACD_hist'] = compute_macd(df['Close'])
        return df

    def compute_rsi(series, window=14):
        delta = series.diff(1)
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=window, min_periods=1).mean()
        avg_loss = loss.rolling(window=window, min_periods=1).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def compute_macd(series, short_window=12, long_window=26, signal_window=9):
        short_ema = series.ewm(span=short_window, adjust=False).mean()
        long_ema = series.ewm(span=long_window, adjust=False).mean()
        macd = short_ema - long_ema
        signal = macd.ewm(span=signal_window, adjust=False).mean()
        hist = macd - signal
        return macd, signal, hist

    price_data = price_data.groupby('Stock').apply(add_technical_indicators)
    # price_data.reset_index(inplace=True, drop=False)

    label_encoder = LabelEncoder()
    price_data['Stock'] = label_encoder.fit_transform(price_data['Stock'])

    # scale the data
    scaler = StandardScaler()
    features_to_scale = ['Open', 'High', 'Low', 'Close', 'Volume', 'MA_10', 'MA_50', 'RSI', 'MACD', 'MACD_signal',
                         'MACD_hist']
    price_data[features_to_scale] = scaler.fit_transform(price_data[features_to_scale])
    # drop the gmtoffset and datetime columns
    price_data.drop(columns=['Gmtoffset', 'Datetime'], inplace=True)

    output_filename = './price_data'
    price_data.to_csv(output_filename + '.csv', index=False)
    price_data.to_hdf(output_filename + '.h5', key='data', mode='w')

    print('Raw data saved, creating sequences...')
    # create look back sequences
    sequences = []

    def create_sequences(data, seq_length):
        sequences = []
        for i in range(len(data) - seq_length):
            seq = data.iloc[i:i + seq_length]
            target = data['Close'].iloc[i + seq_length]  # Assuming 'Close' is the target variable
            sequences.append((seq.values, target))
        return sequences

    for stock in price_data['Stock'].unique():
        stock_data = price_data[price_data['Stock'] == stock]
        stock_sequences = create_sequences(stock_data, lookback_window)
        sequences.extend(stock_sequences)

    X, y = zip(*sequences)
    X = np.array(X)
    y = np.array(y)

    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

    np.savez_compressed('./price_data.npz', X_train=X_train, y_train=y_train, X_val=X_val, y_val=y_val, X_test=X_test,
                        y_test=y_test)
    print('Shape of X_train:', X_train.shape, '\nShape of y_train:', y_train.shape, '\nShape of X_val:', X_val.shape,
          '\nShape of y_val:', y_val.shape, '\nShape of X_test:', X_test.shape, '\nShape of y_test:', y_test.shape)


if __name__ == '__main__':
    build_price_data()
