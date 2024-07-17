# Capstone Project

---
## Project structure
```
├─config.ini  # You may refer to the shared data folder for how to setup config.ini
├─README.md
├─utils.py
├─src
|  ├─predict.py
|  ├─__init__.py
|  ├─model
|  |   ├─model.ipynb
|  |   ├─models.py
|  |   ├─__init__.py
|  |   ├─ckpts
|  ├─img
├─service
|    ├─analysis_service.py
|    ├─orchestra.py
|    ├─prompts.py
|    └README.md
├─data
|  ├─data_cleaner.py
|  ├─download_data.py
|  ├─find_limit.py
|  ├─nasdaq100.html
|  ├─news_check_repeat.py
|  ├─news_process.py
|  ├─README.md
|  ├─json_eodhd    # saving the json data (news data)
|  |     ├─news
|  |     ├─fundamental
|  |     ├─filtered
|  |     ├─cleaned
|  ├─csv_eodhd    # saving the csv data (price data)
|  |     ├─price
|  |     ├─fundamental
├─api
|  ├─eodhd_fundamental_api.py
|  ├─eodhd_hist_news_api.py
|  └eodhd_hist_price_api.py
``` 

## How to run
Start a virtual env of Python, install the requirements by 
```
pip install -r requirements.txt
```
You are suggested to use Python 3.11.

### Download archieved data
Download data from [Here](https://drive.google.com/drive/folders/1MiZQ7roZ90wdJhdWwmZN5nRb0b0BkWZE?usp=drive_link). Please read the README.md file in the shared folder first.
Unzip the file to correct location, you may refer to the file structure above. (./data/)

if you want to download data with different time range or different market. Please refer to the next section.

### Download data from Provider [Optional]
Setup the `config.ini` according to the sample in the shared folder. And then run the script `/data/download_data.py`  

### Cleaning, filtering
Run the `data/data_cleaner.py` and `data/data_filter.py`. This will clean the price data, and filter out useful news data, you may decide whether to corp the news if you have a limited GPU vRAM. We 
recommend you to corp the news if you have a GPU with less than 24GB vRAM.  
To find out whether you need to corp the data or not, you can use `find_limit.py`.  
If you decide not to corp the news, instead of running the `data_filter.py`, you can use the `news_check_repeat.py` to just simply wash out the repeated news.  

### News Processing
You should adjust and run the `news_process.py`. Before that, you should make sure the orchestra and GPU node group are running.  

#### orchestra
 Adjust the URL for your orchestra server. You can start the orchestra on local machine: simply start `/service/orchestra.py`, use a seperate terminal, or use nohup to make the server running on backend. You should make sure the ports are open and firewall settings are allowing the 8000.  
If you run the node on server, still you should run the `orchestra.py`. You should make sure the server is accessible by the localmachine on given ports. Change the port or use NGINX reverse proxy for accessing the server if 6006 port is not available.
Please note that the URLs in orchestra.py is no longer available, they are just rented cloud machine and we will not guarantee that the node are still available when you evaluate the project.  

#### GPU nodes
You can use cloud GPU or local GPU, but at least 1 open port to the internet with stable connection should be available. You should add the GPU node address to the `node_urls` list in the orchestra.py or use POST method to /add_nodes entry to add the GPU nodes URL dynamically.  
If a GPU nodes failed, the orchestra will automatically ignore it and will not miss any tasks (or subtasks).  
To startup the GPU service, you should upload the `prompts.py` and `analysis_service.py` to your machine. Install the dependencies and make sure 6006 port are available, change the port or use NGINX reverse proxy for accessing the server if port 6006 is not available. Run the `analysis_service.py` with nohup or screen tool to make the program running.  
You can log out the program output to a file for tracing the potential problem.  

Now, you can run the `news_process.py`, adjust the path to data and the URL to orchestra node if needed.


The news processed summary result will be available under the same directory.

### Model training and prediction
You should use the `/model/model.ipynb` for training and prediction, the workflow is contained in the notebook file.




