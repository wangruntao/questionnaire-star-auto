import random

import psutil
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import config
api = config.api
def setup_driver(user_agent):
    # 通过API链接爬取IP，这里根据自己的情况进行修改
    # 打印IP列表
    # print(ip_list)
    service = Service(config.driver_path)
    options = Options()
    if config.use_api_proxy:
        response = requests.get(api)
        # 解析JSON数据
        data = response.json()
        # 提取IP列表
        ip_list = [item['ip'] for item in data.get('data', {}).get('list', [])]
        options.add_argument('--proxy-server=http://{}'.format(ip_list[random.randint(0, len(ip_list) - 1)]))
    if config.use_local_proxy:
        options.add_argument('--proxy-server=http://localhost:7890')
    options.add_argument("--no-sandbox")
    # options.add_argument("")
    if config.headless:
        options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    # options.add_argument(f"user-agent={user_agent}")
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(service=service, options=options)
    # 将webdriver属性置为undefined
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })

    chromedriver_process = psutil.Process(driver.service.process.pid)
    print(f"Chromedriver PID: {chromedriver_process.pid}")

    # 返回driver和PID
    return driver, chromedriver_process.pid