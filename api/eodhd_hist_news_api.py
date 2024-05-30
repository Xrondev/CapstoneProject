"""
Functions for getting the historical news, given the stock symbols
"""

import requests
from utils import read_config, write_json


def get_historical_news(symbol: str, from_date: str, to_date: str, limit=50, offset=0, save=True,
                        exchange_id: str = 'US') -> list:
    """
    Get historical news of given symbol, https://eodhd.com/financial-apis/stock-market-financial-news-api/

    :param exchange_id: exchange id, default US
    :param symbol: stock symbol
    :param from_date: start date, format: 'YYYY-MM-DD'
    :param to_date: end date
    :param limit: number of news to get, default 50
    :param offset: offset of the news, default 0
    :param save: if true save to json file, default true, under {project root}/data/json_eodhd
    :return: a list of news
    """
    import re
    if not re.match(r'\d{4}-\d{2}-\d{2}', from_date) or not re.match(r'\d{4}-\d{2}-\d{2}', to_date):
        raise ValueError('Date format should be YYYY-MM-DD')

    config = read_config()
    token = config['TOKEN']['eodhd_token']
    url = f'https://eodhd.com/api/news?s={symbol}.{exchange_id}&from={from_date}&to={to_date}&offset={offset}&limit={limit}&api_token={token}&fmt=json'
    data = requests.get(url).json()
    if save:
        write_json(data, f'news_{symbol.replace(".", "_")}_{from_date}_{to_date}.json', 'data/json_eodhd')
    return data


def test_historical_news():
    url = f'https://eodhd.com/api/news?s=AAPL.US&offset=0&limit=10&api_token=demo&fmt=json'
    data = requests.get(url).json()
    write_json(data, 'test_historical_news.json', 'data/json_eodhd')
    print(data)


if __name__ == '__main__':
    test_historical_news()
