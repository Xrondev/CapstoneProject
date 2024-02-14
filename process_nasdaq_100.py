"""
Process the NASDAQ 100 index info page, retrieved from https://www.slickcharts.com/nasdaq100
2024-02-14, saved as nasdaq_100.html
"""


def get_symbol_name_dict() -> dict:
    """
    Get the stock symbol and company name of NASDAQ 100 index
    :return: a dict like {'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft Corporation', ...}
    """
    from lxml import etree

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
    return result


if __name__ == "__main__":
    get_symbol_name_dict()
    print('Done')
