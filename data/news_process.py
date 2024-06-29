import os
import json
import requests

# Only the following stock codes will be processed
process_stock = ['AAPL', 'META', 'MSFT', 'NVDA', 'AMZN']

news_folder = './json_eodhd/filtered/'

# Define the URL of the sentiment analysis service
service_url = 'https://u11820-9171-93a7ec0f.westc.gpuhub.com:8443/chat'


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


def analyze_sentiment(target: str, content: str):
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    response = requests.request('POST', service_url, headers=headers, data=json.dumps({
        "message": {
            "role": "user",
            "content": f"[Target]{target} \n [NewsContent] {content}"
        }
    }))
    return response.json()


def verify_response(response):
    if response.get("functionality") == "analysis" and "response" in response:
        response_content = response['response'].get("content", "")
        if response_content.startswith("[RANK]:") and "[Explain]:" in response_content:
            try:
                rank_str = response_content.split("[RANK]:")[1].split("\n")[0].strip()
                rank = float(rank_str)
                explanation = response_content.split("[Explain]:")[1].strip()
                if -1 <= rank <= 1 and isinstance(explanation, str):
                    return rank, explanation, None
            except (ValueError, IndexError):
                return None, None, 'rank or explanation not detected in response'
    elif response.get("detail") is not None:
        return None, None, 'Server error' + response.get('detail')
    else:
        return None, None, 'Request error' + response.get('detail')


def process_news_data(target, news_data, output_file):
    error_counter = 0
    for item in news_data:
        # Every historical news item
        # print(item)
        content = item.get('content', '')
        if content:
            response = analyze_sentiment(target=target, content=content)

            rank, explanation, error = verify_response(response)
            if error is None:
                result = {
                    "date": item.get('date'),
                    "title": item.get('title'),
                    "rank": rank,
                    "explanation": explanation,
                    "response": response
                }
            else:
                error_counter += 1
                result = {
                    "date": item.get('date'),
                    "title": item.get('title'),
                    "info": error
                }
            save_result_to_file(result, output_file)  # Save after processing each item
    print(f'ERROR Process counter for {target}: {error_counter} / {len(news_data)}')


def save_result_to_file(result, output_file):
    with open(output_file, 'a', encoding='utf-8') as file:
        file.write(json.dumps(result, ensure_ascii=False) + '\n')


def combine_results(output_file):
    with open(output_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    results = [json.loads(line) for line in lines]
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)


def main():
    news_files = get_news_json_file(news_folder)
    print('files', news_files)

    with open('./nasdaq100_symbol_name.json', 'r') as file:
        company_name_dict = json.load(file)

    for filename in news_files:
        news_data = read_json(filename)
        output_file = f'analysis_result_{filename.split("_")[2]}.json'
        process_news_data(target=company_name_dict.get(filename.split('_')[2]), news_data=news_data,
                          output_file=output_file)
        combine_results(output_file)  # Combine results into a proper JSON array


if __name__ == '__main__':
    main()
