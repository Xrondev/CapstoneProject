"""
API for fundamental data, https://eodhistoricaldata.com/financial-apis/fundamental-data-api/
"""

import requests

from utils import read_config


def get_fundamental(symbol: str, exchange_id: str = 'US'):
    config = read_config()
    token = config['TOKEN']['eodhd_token']
    url = f'https://eodhd.com/api/fundamentals/{symbol}.{exchange_id}?api_token={token}&fmt=json'
    data = requests.get(url).json()

    print(data)
