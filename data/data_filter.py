import json
import math
import os
from urllib.parse import urlparse


def input_file(input_path):
    # read json
    with open(input_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def output_file(data, output_path):
    os.makedirs(output_folder, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as outfile:  # 确保使用 utf-8 编码
        json.dump(data, outfile, indent=4)
    print(f"Filtered data saved to {output_path}. Total items: {len(data)}")

def filter_json_file(data):
    # filter link
    filtered_data = []
    for item in data:
        if 'link' in item:
            parsed_url = urlparse(item['link'])
            domain = parsed_url.netloc
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) > 0 and f"{domain}/{path_parts[0]}" == "finance.yahoo.com/news":
                filtered_data.append(item)
    return filtered_data

def cut_json_file(data):
    cut_data = []
    for index, item in enumerate(data):
        news = item['content'].lower()
        cut_news = None
        # length greater than 9000
        if len(news) >= 9000:
            first_position = news.find("apple")
            last_position = news.rfind("apple")
            if last_position - first_position < 9000 and first_position != -1:  # 关键字间距小于9000，取中值
                mid_position = math.floor((first_position + last_position) / 2)
                if mid_position > 4500:
                    cut_news = news[mid_position - 4500:mid_position + 4500]
                else:
                    cut_news = news[0:mid_position + 4500]
            # displace of keywords greater than 9000
            elif last_position - first_position >= 9000:
                mid_position = first_position
                if mid_position > 4500:
                    cut_news = news[mid_position - 4500:mid_position + 4500]
                else:
                    cut_news = news[0:mid_position + 4500]
            elif first_position == -1:
                print(index, 'no keyword')
                continue
        else:
            cut_data.append(item)

        if cut_news:
            item['content'] = cut_news
            cut_data.append(item)
    return cut_data



input_folder = r'C:\Users\Administrator\Desktop\filtered-unique_news'
output_folder = r'C:\Users\Administrator\Desktop\cut_filtered-unique_news'


for filename in os.listdir(input_folder):
    if filename.endswith('.json'):
        file_path = os.path.join(input_folder, filename)
        data = input_file(file_path)
        cut_data = cut_json_file(data)
        output_file(cut_data, output_folder + '\\' + 'cut_' + filename)




