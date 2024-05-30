"""
Useful functions for the project
"""

import configparser
import os

from lxml import etree


def read_config() -> configparser.ConfigParser:
    """
    Read the config file and return the config object
    :return:
    """
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    # print(config.sections())
    # convert date to timestamp
    import datetime
    for key in config['DATE']:
        config['DATE'][key] = str(datetime.datetime.strptime(config['DATE'][key], '%Y-%m-%d').timestamp())

    return config


def write_json(data, filename: str, relative_path: str = 'data/json_eodhd') -> None:
    """
    Write data to a json file under project root and given relative path
    :param data: json data
    :param filename: filename, ends with .json
    :param relative_path: path relative to project root
    :return: None
    """

    import json
    import os

    project_root = os.path.dirname(__file__)

    if not os.path.exists(os.path.join(project_root, relative_path)):
        os.makedirs(os.path.join(project_root, relative_path))

    with open(os.path.join(project_root, relative_path, filename), 'w') as f:
        json.dump(data, f, indent=4)
    print('Data has been written to', filename)


def get_symbol_name_dict() -> dict:
    """
    Get the stock symbol and company name of NASDAQ 100 index
    :return: a dict like {'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft Corporation', ...}
    """

    page_path = './data/nasdaq100.html'
    with open(page_path, 'r') as f:
        page = f.read()
    page = etree.HTML(page)
    # The table element, tbody
    table = page.xpath('/html/body/div[2]/div[3]/div[1]/div/div/table/tbody')[0]
    result = {}
    for tr in table:
        # iterate through each row
        tds = tr.xpath('td')

        # index, sorted by weight
        # idx = tds[0].text
        # company name
        name = tds[1].xpath('a')[0].text
        # symbol
        symbol = tds[2].xpath('a')[0].text
        result[symbol] = name
    print(result)

    write_json(result, 'nasdaq100_symbol_name.json', 'data/')
    return result


def from_json(filename: str, relative_path: str = 'data/json_eodhd') -> dict:
    """
    Read data from a json file under project root and given relative path
    :param filename: filename, ends with .json
    :param relative_path: path relative to project root
    :return: json data
    """

    import json
    import os

    project_root = os.path.dirname(__file__)

    with open(os.path.join(project_root, relative_path, filename), 'r') as f:
        data = json.load(f)
    return data


if __name__ == '__main__':
    # read_config()
    # write_json({'a': 1, 'b': 2}, 'test.json')
    get_symbol_name_dict()
