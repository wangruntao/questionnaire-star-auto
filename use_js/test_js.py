import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

# 设置 ChromeDriver 的路径（如果没有添加到 PATH）
service = Service(executable_path=r"C:\Users\11575\Downloads\chromedriver-win64\chromedriver.exe")

# 配置浏览器选项
options = Options()
options.add_argument("--disable-notifications")  # 禁用通知

# 初始化 WebDriver
driver = webdriver.Chrome(service=service, options=options)

# 打开目标网页
driver.get("https://www.wjx.cn/vm/eRESiE2.aspx#")

# 从文件读取 JavaScript
with open('wjx-auto.js', 'r', encoding='utf-8') as file:
    script = file.read()

driver.execute_script(script)
# Wait for AJAX calls to complete
WebDriverWait(driver, 10).until(
    lambda driver: driver.execute_script("return jQuery.active == 0;")
)
# 可以在这里添加更多操作，例如等待元素加载、填写表单等
time.sleep(10000)
# 关闭浏览器
driver.quit()
