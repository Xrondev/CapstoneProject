import os

import requests

from utils import read_config, write_json


def get_historical_intraday_price(symbol: str, from_date: str, to_date: str, exchange_id: str = 'US',
                                  interval: str = "1h", save=True) -> list:
    """
    Get the historical intraday price of given symbol stock in the given exchange, https://eodhd.com/financial-apis/intraday-historical-data-api/
    :param symbol: stock symbol
    :param exchange_id: exchange id, default US
    :param from_date: start date, should be configured in config.ini, read from config and util will convert it into timestamp
    :param to_date: end date
    :param interval: price interval, '1m', '5m' or '1h'
    :param save: if true save to json file, default true, under {project root}/data/json_eodhd
    :return:
    """

    config = read_config()
    token = config['TOKEN']['eodhd_token']
    url = (f'https://eodhd.com/api/intraday/{symbol}.{exchange_id}?api_token={token}&from={from_date}&to={to_date}'
           f'&interval={interval}&fmt=csv')
    data = requests.get(url)

    if save:
        # json
        # write_json(data, f'price_{symbol.replace(".", "_")}_{from_date}_{to_date}_{interval}.json', 'data/json_eodhd')
        os.makedirs('../data/csv_eodhd/price/', exist_ok=True)
        # csv save
        if data.status_code == 200:
            import datetime
            # turn to yyyy-mm-dd
            f_d = datetime.datetime.fromtimestamp(float(from_date)).strftime('%Y-%m-%d')
            t_d = datetime.datetime.fromtimestamp(float(to_date)).strftime('%Y-%m-%d')
            with open(f'../data/csv_eodhd/price/price_{symbol.replace(".", "_")}_{f_d}_{t_d}_{interval}.csv',
                      'wb') as f:
                f.write(data.content)
                print(f'{symbol} historical price written')
    return data


# Current work on this API, if not capable for our project, we can switch to End of Day price API
# + potential to do: End of Day API wrap

def test_historical_price():
    url = f'https://eodhd.com/api/intraday/AAPL.US?interval=5m&api_token=demo&fmt=csv'
    data = requests.get(url).json()
    write_json(data, 'test_historical_price.json', 'data/json_eodhd')
    print(data)


if __name__ == '__main__':
    test_historical_price()
