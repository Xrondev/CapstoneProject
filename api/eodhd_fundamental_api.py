"""
API for fundamental data, https://eodhistoricaldata.com/financial-apis/fundamental-data-api/
"""
import os

import requests

from utils import read_config


def get_fundamental(symbol: str, exchange_id: str = 'US', save=True):
    config = read_config()
    token = config['TOKEN']['eodhd_token']
    url = f'https://eodhd.com/api/fundamentals/{symbol}.{exchange_id}?api_token={token}&fmt=json'
    data = requests.get(url)

    if save:
        os.makedirs('../data/json_eodhd/fundamental/', exist_ok=True)
        # csv save
        if data.status_code == 200:
            with open(f'../data/json_eodhd/fundamental/fundamental_{symbol.replace(".", "_")}.json',
                      'wb') as f:
                f.write(data.content)
                print(f'{symbol} fundamental data written')
    return data
