import joblib
import numpy as np
import pandas as pd
import glob

from sklearn.model_selection import train_test_split


def build_price_data():
    def load_data_with_stock_name(file):
        df = pd.read_csv(file)
        stock_name = file.split('/')[-1].split('_')[1]  # Extract stock name from the file name
        df['unique_id'] = stock_name  # rename the stock to unique_id
        return df

    # Load all CSV files into a single DataFrame
    price_files = glob.glob('./csv_eodhd/price/*.csv')
    price_dfs = [load_data_with_stock_name(file) for file in price_files]
    price_data = pd.concat(price_dfs, ignore_index=True)

    price_data['Timestamp'] = pd.to_datetime(price_data['Timestamp'], unit='s')
    price_data['week_day'] = price_data['Timestamp'].dt.weekday  # 0 for Monday

    price_data.drop(columns=['Timestamp', 'Gmtoffset'],
                    inplace=True)  # drop the raw data Timestamp and Gmtoffset column
    price_data.rename(columns={'Close': 'y', 'Datetime': 'ds'}, inplace=True)

    price_data.sort_values(by=['unique_id', 'ds'], inplace=True)

    # convert the datestamp into int, or else the plotting will be strange (7 hrs per day and other hrs data is empty)
    price_data['ds'] = price_data.groupby('unique_id').cumcount()


    price_data.fillna(method='ffill', inplace=True)

    price_data.to_csv('./price.csv')


if __name__ == '__main__':
    build_price_data()
