import json

import matplotlib.pyplot as plt

from data.news_process import analyze_sentiment

file_path = './json_eodhd/filtered/filtered-unique_news_AAPL_2020-10-21_2024-05-30.json'

with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

content = data[23].get('content')
print(len(content))


def find_max_len():
    def is_processable(content, length):
        truncated_content = content[:length]
        response = analyze_sentiment(target='Apple', content=truncated_content)
        print(response)
        return response.get('detail') is None

    # l, r = 0, len(content)
    max_length = 0
    l, r = 0, 9000
    if is_processable(content, r - l):
        max_length = r - l

    # while l <= r:
    #     mid = (l + r) // 2
    #     if is_processable(content, mid):
    #         max_length = mid
    #         l = mid + 1
    #     else:
    #         r = mid - 1

    print(f'Max length: {max_length}')
    return max_length


def statistics_news_content_len():
    content_len = []
    for item in data:
        content = item.get('content')
        content_len.append(len(content))

    from matplotlib import pyplot as plt

    plt.figure(figsize=(16, 9))
    plt.bar(x=range(len(content_len)), width=1, height=content_len)
    plt.show()

    return content_len


if __name__ == '__main__':
    # result = []
    # for i in range(0, 10):
    #     result.append(find_max_len())
    # print(result)
    # plt.figure(figsize=(16, 9))
    # plt.bar(x=range(len(result)), width=1, height=result)
    # plt.show()
    cl = statistics_news_content_len()
    print(f'{sum([i > 9000 for i in cl]) / len(cl):.4f} % news exceeded the max len')