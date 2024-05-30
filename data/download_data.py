"""
Download different data here

1. historical price data **
2. historical news data
3. historical volume data
"""

from api.eodhd_hist_price_api import get_historical_intraday_price
from utils import read_config, from_json


def d():
    config = read_config()
    from_date = config['DATE']['from']
    to_date = config['DATE']['to']

    # get historical intraday price data
    for symbol, name in from_json('nasdaq100_symbol_name.json', './data').items():
        print('Historical intraday price data for', symbol, ':', name)
        get_historical_intraday_price(symbol, from_date, to_date, save=True)



if __name__ == '__main__':
    d()
