class Data:
    """
    Read from json files, return corresponding data.
    """
    def __init__(self, symbol: str):
        self.symbol = symbol

    def get_historical_news(self):
        return NotImplementedError

    def get_daily_news_iterator(self) -> iter:
        return NotImplementedError

    # ...