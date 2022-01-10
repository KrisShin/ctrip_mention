# Ctrip Mention Script

Auto get cheape ticket and send a notification by WeChat.(5 times per day)


## Install dependency packages

```python
pip install lxml urllib3 requests selenium
```


## WeChat Notification Push Service

Thanks for supply servece api by [server酱](https://sct.ftqq.com/).

Please get your personal sendKey from [server酱](https://sct.ftqq.com/).


## Modify code

#### Modify the sendKey, please get your personal sendKey from [server酱](https://sct.ftqq.com/).

```python
WECHAT_MSG_URL = 'https://sctapi.ftqq.com/yourSendKey.send'
```

#### get your chromedriver
Put your chromedriver into drivers.
Modify line 161 to your chromedriver path.
```python
driver = webdriver.Chrome(
    executable_path="./drivers/chromedriver_linux", options=options
    # executable_path="./drivers/chromedriver", options=options
)
```


## Launch params

> -leave: set off code, you can get it from https://ctrip.com.

> -reach: arrive city code

> -date: set off date (format: 2022-01-01)

> -price: target price of ticket


## Launch Scripts

```shell
python ctrip_spider.py -leave CTU -reach SHA -date 2022-01-01 -price 1000
```