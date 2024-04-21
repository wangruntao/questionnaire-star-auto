import random

import psutil
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import config


def setup_driver(user_agent):
    # 通过API链接爬取IP，这里根据自己的情况进行修改
    # 打印IP列表
    # print(ip_list)
    service = Service(config.driver_path)
    options = Options()
    if config.use_api_proxy:
        response = requests.get(config.api)
        # 解析JSON数据
        data = response.json()
        # 提取IP列表
        ip_list = [item['ip'] for item in data.get('data', {}).get('list', [])]
        options.add_argument('--proxy-server=http://{}'.format(ip_list[random.randint(0, len(ip_list) - 1)]))
    if config.use_local_proxy:
        options.add_argument('--proxy-server=http://localhost:7890')
    if config.use_proxy_pool:
        print("使用代理")
        # url = 'http://zltiqu.pyhttp.taolop.com/getip?count=16&neek=103463&type=2&yys=0&port=1&sb=&mr=1&sep=0&ts=1&regions=110000,320000,370000,450000,500000,410000,330000,130000,150000,340000,420000,510000,520000,430000,350000,210000,220000,360000,440000,610000'
        proxy_data = config.proxy_data
        # 随机选择一个代理
        selected_proxy = random.choice(proxy_data['data'])
        proxy_server = f"http://{selected_proxy['ip']}:{selected_proxy['port']}"
        options.add_argument(f'--proxy-server={proxy_server}')
    options.add_argument("--no-sandbox")
    # options.add_argument("")
    if config.headless:
        options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(service=service, options=options)
    # 将webdriver属性置为undefined
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })

    chromedriver_process = psutil.Process(driver.service.process.pid)
    # print(f"Chromedriver PID: {chromedriver_process.pid}")

    # 返回driver和PID
    return driver, chromedriver_process.pid
