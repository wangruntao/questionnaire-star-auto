from selenium import webdriver

# 远程Docker服务的地址和端口
#wd 表示 WebDriver，hub 表示服务器的入口点。
#通过在 URL 中指定 /wd/hub，您告诉 Selenium 客户端要连接到远程的 WebDriver 服务器
#服务器9516映射到docker中4444端口也就是Webdriver-selenim服务端口
ip = '127.0.0.1'
remote_url = f'http://{ip}:9516/wd/hub'
print(remote_url)
# 配置浏览器选项
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# 连接到远程Selenium Chrome节点
driver = webdriver.Remote(command_executor=remote_url, options=chrome_options)

# 打开浏览器
driver.get('https://www.baidu.com')

# 关闭浏览器
<<<<<<< HEAD
# driver.quit()