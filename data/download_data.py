"""
Download different data here

1. historical price data **
2. historical news data
3. historical volume data
"""
from api.eodhd_hist_news_api import get_historical_news
from api.eodhd_hist_price_api import get_historical_intraday_price
from api.eodhd_fundamental_api import get_fundamental
from utils import read_config, from_json

data_partition = {
    'price': False,
    'news': True,
    'fundamental': False,
}


def d():
    config = read_config()
    from_date = config['DATE']['from']
    to_date = config['DATE']['to']

    stock_list = from_json('nasdaq100_symbol_name.json', './data')
    cnt = 0
    # get historical intraday price data
    for symbol, name in stock_list.items():
        cnt += 1

        print(f'[{cnt}/{len(stock_list)}] Getting data for {symbol}...')
        if data_partition['price']:
            get_historical_intraday_price(symbol, from_date, to_date, save=True)
        if data_partition['news']:
            get_historical_news(symbol, from_date, to_date, save=True, limit=1000)
        if data_partition['fundamental']:
            get_fundamental(symbol, save=True)


if __name__ == '__main__':
    d()
