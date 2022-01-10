# 机票提醒服务

自动获取低价机票并发送微信通知(每天五次)


## 安装第三方依赖包

```python
pip install lxml urllib3 requests selenium
```


## 微信通知服务

感谢[server酱](https://sct.ftqq.com/)提供的微信通知服务API

请到[server酱](https://sct.ftqq.com/)官网获取sendKey



## 修改代码

#### 修改sendKey, 请到[server酱](https://sct.ftqq.com/)官网获取sendKey

```python
WECHAT_MSG_URL = 'https://sctapi.ftqq.com/你的sendKey.send'
```

#### 选择对应系统的chromedriver
将你的Chrome浏览器对应版本的chromedriver放入drivers目录中
修改161行 为你自己的chromedriver路径
```python
driver = webdriver.Chrome(
    executable_path="./drivers/chromedriver_linux", options=options
    # executable_path="./drivers/chromedriver", options=options
)
```


## 启动参数

> -leave: 出发城市代码, 可以打开ctrip.com搜索出发城市获取出发城市代码

> -reach: 到达城市代码 

> -date: 出发时间, 会自动获取前后一天时间的机票(格式: 2022-01-01), 

> -price: 目标票价


## 启动脚本

```shell
python ctrip_spider.py -leave CTU -reach SHA -date 2022-01-01 -price 1000
```