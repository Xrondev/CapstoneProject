import os
import json
import time
import requests

# Only the following stock codes will be processed
process_stock = ['AAPL', 'META', 'MSFT', 'NVDA', 'AMZN']

news_folder = './json_eodhd/filtered/'

# Define the URL of the orchestra node
service_url = 'http://localhost:8000'


def get_news_json_file(folder: str):
    files = []
    for filename in os.listdir(folder):
        if filename.endswith('.json') and any(stock in filename for stock in process_stock) and 'unique' in filename:
            files.extend([filename])
    return files


def read_json(filename: str):
    with open(os.path.join(news_folder, filename), 'r', encoding='utf-8') as file:
        data = json.load(file)
        print(len(data))
        return data


def analyze(target: str, content: str, current_task_id: int, total_task_id: int):
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    attempt = 0
    while attempt < 3:
        response = requests.post(f'{service_url}/process', headers=headers, json={
            "message": {
                "role": "user",
                "content": f"[Target]{target} \n [NewsContent] {content}"
            },
            "task_id": f"{current_task_id}/{total_task_id}",
            "target": target
        })
        if response.status_code == 200:
            return
        attempt += 1
        time.sleep(5)


def check_queue_size():
    response = requests.get(f'{service_url}/queue_size')
    queue_data = response.json()
    queue_size = queue_data.get('queue_size', 0)
    print(f'Queue size: {queue_size}')
    return queue_size


def process_news_data(target, news_data):
    total_task_count = len(news_data)
    for idx, item in enumerate(news_data):

        # start from index 5000?
        if idx < 5000:
            continue

        content = item.get('content', '')
        if content:
            # Check queue size before processing a new item
            while True:
                queue_size = check_queue_size()
                if queue_size <= 10:
                    analyze(target, content, idx + 1, total_task_count)
                    break
                else:
                    print('Waiting for queue size to drop...')
                    time.sleep(5)


def main():
    news_files = get_news_json_file(news_folder)
    print('files', news_files)

    with open('./nasdaq100_symbol_name.json', 'r') as file:
        company_name_dict = json.load(file)

    for filename in news_files:
        news_data = read_json(filename)
        target = company_name_dict.get(filename.split('_')[2], 'Unknown')
        process_news_data(target, news_data)


if __name__ == '__main__':
    main()
