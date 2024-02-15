import requests

from utils import read_config, write_json


def get_historical_intraday_price(symbol: str, from_date: str, to_date: str, exchange_id: str = 'US',
                                  interval: str = "1h", save=True) -> list:
    """
    Get the historical intraday price of given symbol stock in the given exchange, https://eodhd.com/financial-apis/intraday-historical-data-api/
    :param symbol: stock symbol
    :param exchange_id: exchange id, default US
    :param from_date: start date, 7200 days for 1h interval, format: 'YYYY-MM-DD'
    :param to_date: end date
    :param interval: price interval, '1m', '5m' or '1h'
    :param save: if true save to json file, default true, under {project root}/data/json_eodhd
    :return:
    """
    import re
    if not re.match(r'\d{4}-\d{2}-\d{2}', from_date) or not re.match(r'\d{4}-\d{2}-\d{2}', to_date):
        raise ValueError('Date format should be YYYY-MM-DD')

    config = read_config()
    token = config['TOKEN']['eodhd_token']
    url = (f'https://eodhd.com/api/intraday/{symbol}.{exchange_id}?api_token={token}&from={from_date}&to={to_date}'
           f'&interval={interval}&fmt=json')
    data = requests.get(url).json()
    if save:
        write_json(data, f'price_{symbol.replace(".", "_")}_{from_date}_{to_date}_{interval}.json', 'data/json_eodhd')
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
