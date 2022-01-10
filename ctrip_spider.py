import argparse
from collections import defaultdict
from lxml import etree
from time import sleep
from datetime import date, datetime, timedelta
import urllib3
import requests as r
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

options = Options()
# 设置 webdriver 无头运行
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
# 初始化 webdriver
# driver = webdriver.Chrome(
#     executable_path="./drivers/chromedriver.exe",
#     chrome_options=chrome_options,
# )

WECHAT_MSG_URL = 'https://sctapi.ftqq.com/xxx.send'
SEND_COUNT = 5
# 屏蔽 https 证书报警信息
urllib3.disable_warnings()

# 定义 session  请求头，设置 UA
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
}

# 定义异常数量全局变量
EXCEPTION_COUNT = 0
# 定义异常最大值全局变量
MAX_EXCEPTION_COUNT = 1000

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument("-leave", type=str, default="SHA")
parser.add_argument("-reach", type=str, default="CTU")
parser.add_argument("-date", type=str, default="2022-01-28")
parser.add_argument("-price", type=float, default=0)
args = parser.parse_args()

LEAVE_LOCATION = args.leave.upper()
REACH_LOCATION = args.reach.upper()
TARGET_DATE = [int(x) for x in args.date.split('-')]
TARGET_PRICE = args.price
DATE_LIST = [str(date(*TARGET_DATE))] + [
    str(date(*TARGET_DATE) + timedelta(days=x)) for x in (-1, 1)
]

result = defaultdict(list)
# mention_list = defaultdict(list)

# 记录抓取异常
def record_exception_count(err):
    print(err)
    global EXCEPTION_COUNT
    EXCEPTION_COUNT += 1
    # 抓取异常次数达到最大值时抛出异常
    if EXCEPTION_COUNT > MAX_EXCEPTION_COUNT:
        print("exceed max exception count")
        raise RuntimeError


# 初始化 chromedriver 获取首页 cookie
def init_driver(date, driver):
    driver.get(
        f"https://m.ctrip.com/html5/flight/swift/domestic/{LEAVE_LOCATION}/{REACH_LOCATION}/{date}"
    )

    try:
        # waitting for alert dialog.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/ul/li/div')
            )
        )

        btn_known = driver.find_element_by_xpath(
            '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/ul/li/div/div[4]/div'
        )
        btn_known.click()
    except:
        pass

    # scroll to bottom of the page
    sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(5)
    return driver.page_source


def parse_html(date, html, mention_list):
    selector = etree.HTML(html)
    card_list = selector.xpath('//div[@class="card-item-content"]')
    min_price = [999999, 999999, 999999]
    min_three = []
    print(datetime.now(), date, len(card_list))
    for card in card_list:
        try:
            depart_node = card.xpath('div//div[@class="flight-depart"]')[0]
            dest_node = card.xpath('div//div[@class="flight-dest"]')[0]
            price_node = card.xpath('div//div[@class="flight-price"]')[0]
            plane_node = card.xpath('div[@class="flight-plane"]//span/text()')
            middle_node = card.xpath(
                'div/div/div//span[@class="icon-arrow-state"]//span/text()'
            )
            rest_ticket = price_node.xpath('div/span[@class="ticket-inventory"]/text()')
        except Exception as err:
            record_exception_count(err)
            continue

        price = float(price_node.xpath('div[1]/strong/text()')[0])
        if price and price > TARGET_PRICE * 2:
            continue
        data = {
            'depart_time': depart_node.xpath('div[@class="flight-time"]/text()')[
                0
            ].strip(),
            'depart_airport': '-'.join(
                depart_node.xpath('div[@class="flight-airport"]/span/text()')
            ),
            'dest_time': dest_node.xpath('div[@class="flight-time"]/text()')[0].strip(),
            'dest_airport': '-'.join(
                [x.strip() for x in dest_node.xpath('div[2]/span/text()') if x.strip()]
            ),
            'middle': '-'.join(middle_node),
            'price': str(price),
            'rest_ticket': str(rest_ticket and rest_ticket[0].strip()),
            'discount': price_node.xpath('div[2]/text()')[0].strip()
            if price_node.xpath('div[2]/text()')
            else price_node.xpath('div[2]//span[@class="ticket-right"]/text()')[
                0
            ].strip(),
            'airplane': str([x.strip() for x in plane_node if x.strip()]),
        }
        # result[date].append(data)
        if price <= TARGET_PRICE:
            mention_list[date].append(data)
        if price < min_price[0]:
            min_price.insert(0, price)
            min_three.insert(0, data)
        elif price < min_price[1]:
            min_price.insert(1, price)
            min_three.insert(1, data)
        elif price < min_price[2]:
            min_price.insert(2, price)
            min_three.insert(2, data)
        min_price = min_price[:3]
        min_three = min_three[:3]
    if not (mention_list[date] or TARGET_PRICE):
        mention_list[date] = min_three


def run_spider():
    driver = webdriver.Chrome(
        executable_path="./drivers/chromedriver_linux", options=options
        # executable_path="./drivers/chromedriver", options=options
    )
    mention_list = defaultdict(list)
    for date in DATE_LIST:
        page_html = init_driver(date, driver)
        parse_html(date, page_html, mention_list)
        sleep(10)
    driver.quit()
    global SEND_COUNT
    table_data = []
    for date, lines in mention_list.items():
        for line in lines:
            table_data.append(f"| {date} | { ' | '.join(line.values()) } |")
    if not table_data:
        return
    r.post(
        WECHAT_MSG_URL,
        params={
            'title': '有新的航班可以购入',
            'desp': """
| Date | depart_time | depart_airport | dest_time | dest_airport | middle | price | rest_ticket | discount | airplane |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{}
""".format(
                '\n'.join(table_data)
            ),
            'channel': 9,
        },
    )
    SEND_COUNT -= 1


def time_scheduler():
    global SEND_COUNT

    while True:
        if 23 > datetime.now().hour > 8:
            if SEND_COUNT:
                run_spider()
            sleep(30 * 60)
            continue
        print("day off")
        SEND_COUNT = 5
        sleep(30 * 60)


if __name__ == '__main__':
    time_scheduler()
