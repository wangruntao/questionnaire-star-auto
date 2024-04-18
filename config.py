import requests

from utils import get_url_content

# 目标网址
url = 'https://www.wjx.cn/vm/Pi4VOMa.aspx?open_in_browser=true'  # 护士
# debug = True
debug = False
use_proxy_pool = True
# use_proxy_pool = False
# 线程数，份数
thread_num = 8
epoch = 100
sleep_time = 2

task_list = [{
    'url': 'https://www.wjx.cn/vm/eYL1evZ.aspx',  # 初中生
    'prob': {
        1: [2, 8],
        2: [3, 3, 3, 1]
        # 3: [13, 14, 15],
        # 5: [1, 2, 1],
        # 6: [4, 3, 1, 1],
        # 7: [3, 3, 2, 1, 1],
        # 8: [1, 1, 2, 2, 3]
    },
    'num': 140
}, ]

# 什么类型的问卷
type = 1
if '/vm/' in url:
    type = 2
elif '/vj/' in url:
    type = 1
else:
    type = 0  # 默认值或其他情况
proxy_data = {}
# 远程ip池
api = "http://zltiqu.pyhttp.taolop.com/getip?count=500&neek=103463&type=2&yys=0&port=1&sb=&mr=1&sep=0&ts=1&regions=410000"
if use_proxy_pool:
    proxy_data = requests.get(api).json()
# 是否隐藏浏览器
headless = False
# headless = True

# 使用代理？
use_api_proxy = False
# use_api_proxy = True
# use_local_proxy = True
use_local_proxy = False

# IP API提取链接 https://xip.ipzan.com/ 这个每周都有几百个免费的IP代理领取


# User-Agent库
UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (Linux; Android 10; SEA-AL10 Build/HUAWEISEA-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/4313 MMWEBSDK/20220805 Mobile Safari/537.36 MMWEBID/9538 MicroMessenger/8.0.27.2220(0x28001B53) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 8 Pro Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/045913 Mobile Safari/537.36 V1_AND_SQ_8.8.68_2538_YYB_D A_8086800 QQ/8.8.68.7265 NetType/WIFI WebP/0.3.0 Pixel/1080 StatusBarHeight/76 SimpleUISwitch/1 QQTheme/2971 InMagicWin/0 StudyMode/0 CurrentMode/1 CurrentFontScale/1.0 GlobalDensityScale/0.9818182 AppId/537112567 Edg/98.0.4758.102",
]

driver_path = r"C:\Users\wrt\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

if debug:
    headless = False
else:
    headless = True
