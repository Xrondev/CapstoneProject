# Capstone Project

---
Under construction


## file structure
> <p>treer -i "/.idea|.venv|.git|__pycache__/"</p>
> # use this command to generate file structure, Node required.
```
.
├─config.ini
├─README.md
├─utils.py                          # utility functions
├─src
|  ├─predict.py
|  ├─model                          # model code will be created here
|  |   └__init__.py
|  ├─backtesting                    # backtesting module
|  |      └__init__.py
├─data
|  ├─data_cleaner.py                # data cleaning
|  ├─feature_engineering.py         # feature engineering
|  ├─nasdaq100.html                 # just a webpage copy for stock symbols
|  ├─json_eodhd
|  |     └test_historical_news.json
├─api
|  ├─eodhd_hist_news_api.py
|  ├─eodhd_hist_price_api.py
|  └llm_api.py
```

