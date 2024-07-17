import json
from datetime import datetime
import pandas as pd


def get_news_date(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    total_items = len(data)

    dates = []

    for item in data:
        date = item.get('date')
        parsed_time = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
        formatted_time = parsed_time.strftime("%Y-%m-%d %H:%M:%S")
        dates.append(formatted_time)

    datelist = []
    for date in dates:
        datelist.append(date)

    return datelist

def get_attributes(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    extracted_results = []
    for item in json_data:
        if item['status'] == 'success':
            rank_value, risk_value, sentiment_value = None, None, None

            if 'result4' in item['results']:
                result4_content = item['results']['result4']
                lines = result4_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('**RANK:**'):
                        parts = line.split(' ')

                        if len(parts) > 1:
                            rank_value = parts[1].strip()
                    elif line.startswith('**RISK:**'):
                        parts = line.split(' ')
                        if len(parts) > 1:
                            risk_value = parts[1].strip()

                    elif line.startswith('**SENTIMENT:**'):
                        parts = line.split(' ')
                        if len(parts) > 1:
                            sentiment_value = parts[1].strip()

            extracted_results.append({
                'task_id': item['task_id'],
                'RANK': rank_value,
                'RISK': risk_value,
                'SENTIMENT': sentiment_value
            })

    return extracted_results

def merge(date,extracted_results):
    combined_data = []

    for timestamp, analysis in zip(date, extracted_results):
        combined_entry = analysis.copy()
        combined_entry['timestamp'] = timestamp
        combined_data.append(combined_entry)
    datelist = combined_data
    for item in datelist:
        if isinstance(item, dict) and 'timestamp' in item:
            pass
        else:
            print("Error: Item is not a dictionary or does not contain 'timestamp' key.")
    datelist.sort(key=lambda x: datetime.strptime(x['timestamp'], '%Y-%m-%d %H:%M:%S'))

    grouped_data = {}
    current_date = None

    daily_limit = 8

    for item in datelist:
        date_str = item['timestamp'].split(' ')[0]
        if date_str != current_date:
            current_date = date_str
            grouped_data[current_date] = []

        if len(grouped_data[current_date]) < daily_limit:
            grouped_data[current_date].append(item)
        else:
            continue

    all_data = []
    for day_data in grouped_data.values():
        all_data.extend(day_data)


    return all_data


def add_to_price(price,combined_data):
    df_original = pd.read_csv(price)

    df_additional = pd.DataFrame(combined_data)
    for i in range(200):
        row = df_additional.iloc[i]
        df_original.loc[i, 'Rank'] = row['RANK']
        df_original.loc[i, 'Risk'] = row['RISK']
        df_original.loc[i, 'Sentiment'] = row['SENTIMENT']

    df_original.to_csv('price1-2.csv', index=False)
    print("Added!")

if __name__ == '__main__':

    file_path = r'D:\torch\hku\CapstoneProject\data\json_eodhd\news\news_AAPL_2024-01-01_2024-02-01.json'
    date = get_news_date(file_path)
    print(date)
    extracted_results = get_attributes('service/result_Unknown2-3.json')
    # print(extracted_results)
    combined_data = merge(date, extracted_results)
    price_data = './data/csv_eodhd/price/price_AAPL_2024-01-01_2024-02-01_1h.csv'
    print(combined_data)
    add_to_price(price_data,combined_data)
