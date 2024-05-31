"""
Functions for getting the historical news, given the stock symbols
"""
import json
import os
import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm
import requests
from utils import read_config, write_json


def get_historical_news(symbol: str, from_date: str, to_date: str, limit=50, offset=0, save=True,
                        exchange_id: str = 'US') -> list:
    """
    Get historical news of given symbol, https://eodhd.com/financial-apis/stock-market-financial-news-api/

    :param exchange_id: exchange id, default US
    :param symbol: stock symbol
    :param from_date: start date, should be configured in config.ini, read from config and util will convert it into timestamp
    :param to_date: end date
    :param limit: number of news to get, default 50
    :param offset: offset of the news, default 0
    :param save: if true save to json file, default true, under {project root}/data/json_eodhd
    :return: a list of news
    """

    def fetch_news_for_period(symbol, exchange_id, start_date, end_date, offset, limit, token):
        url = f'https://eodhd.com/api/news?s={symbol}.{exchange_id}&from={start_date}&to={end_date}&offset={offset}&limit={limit}&api_token={token}&fmt=json'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(
                f'Error getting news for {symbol} from {start_date} to {end_date}, status code: {response.status_code}')
            return []

    config = read_config()
    token = config['TOKEN']['eodhd_token']

    # Convert from_date and to_date to datetime objects
    from_date_dt = datetime.datetime.fromtimestamp(float(from_date))
    to_date_dt = datetime.datetime.fromtimestamp(float(to_date))

    all_news = []

    # Calculate the number of months to iterate through
    num_months = (to_date_dt.year - from_date_dt.year) * 12 + to_date_dt.month - from_date_dt.month + 1

    # Prepare date ranges for each month
    date_ranges = []
    current_date_dt = from_date_dt
    while current_date_dt <= to_date_dt:
        next_month_dt = (current_date_dt.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
        end_date_dt = min(next_month_dt, to_date_dt)
        date_ranges.append((current_date_dt.strftime('%Y-%m-%d'), end_date_dt.strftime('%Y-%m-%d')))
        current_date_dt = next_month_dt

    # Rate limiting parameters
    max_requests_per_minute = 200
    request_count = 0
    start_time = time.time()

    # Fetch news data using multithreading
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(fetch_news_for_period, symbol, exchange_id, start, end, offset, limit, token)
            for start, end in date_ranges
        ]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching historical news"):
            news_data = future.result()
            if news_data:
                all_news.extend(news_data)

            # rate limiting
            request_count += 1
            if request_count >= max_requests_per_minute:
                elapsed_time = time.time() - start_time
                if elapsed_time < 60:
                    time_to_sleep = 60 - elapsed_time
                    print(f"!!!!!Hit RATE LIMIT. Sleeping for {time_to_sleep} seconds.")
                    time.sleep(time_to_sleep)
                # Reset count and start time
                request_count = 0
                start_time = time.time()

    all_news.sort(key=lambda x: x['date'])

    if save:
        os.makedirs('../data/json_eodhd/news/', exist_ok=True)
        f_d = from_date_dt.strftime('%Y-%m-%d')
        t_d = to_date_dt.strftime('%Y-%m-%d')
        with open(f'../data/json_eodhd/news/news_{symbol.replace(".", "_")}_{f_d}_{t_d}.json', 'w') as f:
            json.dump(all_news, f, indent=4)
            print(f'{symbol} historical news written')

    return all_news


def test_historical_news():
    url = f'https://eodhd.com/api/news?s=AAPL.US&offset=0&limit=10&api_token=demo&fmt=json'
    data = requests.get(url).json()
    write_json(data, 'test_historical_news.json', 'data/json_eodhd')
    print(data)


if __name__ == '__main__':
    test_historical_news()
