# 目标网址
url = 'https://www.wjx.cn/vj/wk8Yo2t.aspx'
# url = 'https://www.wjx.cn/vm/ep3aOP1.aspx#'
# url = 'https://www.wjx.cn/vm/QN6L2lI.aspx'


single_choice_questions = {1, 2, 3, 4, 6, 7, 8, 9, 11, 13, 15, 16, 19, 20, 22, 24, 25}
multiple_choice_questions = {5, 10, 12, 14, 17, 18, 21, 23}
# 题项比例，确保选项数量和数组长度一致
# prob = {
#     1: [0.5, 0.5],  # 性别，等概率选择
#     2: [0.25, 0.25, 0.25, 0.25],  # 学历，等概率选择
#     3: [0.9, 0.1],  # 民族，主要选择汉族
#     4: [1, 2, 2, 2, 0, 0],  # 政治面貌，偏重于团员和党员
#     5: [1, 1, 1, 1, 1],  # 经常阅读的题材类型，等概率
#     6: [0, 1, 1, 2, 2, 1, 0],  # 阅读题材研究程度，偏重于中间选项
#     7: [1, 1, 1, 1, 1],  # 对个人成长影响最大的，等概率
#     8: [0.6, 0.4],  # 阅读方式偏好，偏向纸质阅读
#     9: [0, 0, 0.2, 0.2, 0.3, 0.3, 0],  # 纸质阅读频率，偏重于“有时”和“经常”
#     10: [1, 1, 1, 1, 1],  # 纸质阅读内容，等概率
#     11: [0, 0, 0.2, 0.2, 0.3, 0.3, 0],  # 数字阅读频率，偏重于“有时”和“经常”
#     12: [1, 0.5, 0.3, 1, 2, 1, 1],  # 数字阅读使用的媒介，偏重于手机和平板
#     13: [0.4, 0.6],  # 阅读方式舒适度，偏向数字阅读
#     14: [1, 1, 1, 1, 1],  # 阅读时间安排，等概率
#     15: [0.2, 0.2, 0.2, 0.2, 0.1, 0.1],  # 定期阅读规划时间，均衡偏好
#     16: [0.6, 0.4],  # 是否有个人阅读规划，偏向有
#     17: [0.7, 0.3],  # 能否在规划内完成阅读，偏向能
#     18: [1, 1, 1, 1, 1, 1],  # 常用阅读交流方式，等概率
#     19: [0, 0, 0.1, 0.3, 0.3, 0.3, 0],  # 交流方式的研究程度，偏重中间选项
#     20: [1, 1, 1, 1, 1, 1],  # 影响个人成长的交流方式，等概率
#     21: [1, 1, 1, 1, 1, 1],  # 阅读目的，等概率
#     22: [0, 0.1, 0.2, 0.3, 0.2, 0.2, 0],  # 阅读目的的意识强烈程度，平衡偏好
#     23: [1, 1, 1, 1, 1, 1],  # 影响大的阅读目的，等概率
#     24: [0, 0, 0.1, 0.2, 0.3, 0.4, 0],  # 个人阅读习惯，偏向良好和优秀
#     25: [0, 0, 0.1, 0.2, 0.3, 0.4, 0]  # 阅读习惯受大学生活影响的程度，偏向较大和极大
# }








type = 1
if '/vm/' in url:
    type = 2
elif '/vj/' in url:
    type = 1
else:
    type = 0  # 默认值或其他情况

# 远程ip池
api = "https://service.ipzan.com/core-extract?num=10&no=20240413223483271825&minute=1&pool=quality&secret=m2u8fsj071od04"

# 是否隐藏浏览器
headless = False
# headless = True

# 使用代理？
use_api_proxy = False
# use_api_proxy = True
use_local_proxy = True
# use_local_proxy = False

# 线程数，份数
thread_num = 1
epoch = 100
sleep_time = 1

# single_choice_questions = {1, 3, 4, 5, 6}
# multiple_choice_questions = {2}
# prob = {
#     1: [1, 1, 1, 1]
# }
#
prob = {}
# 单选题号 多选题号

# 简答题题库
answerList = {
    6: ["123", "12"]
}
# IP API提取链接 https://xip.ipzan.com/ 这个每周都有几百个免费的IP代理领取


# User-Agent库
UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (Linux; Android 10; SEA-AL10 Build/HUAWEISEA-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/4313 MMWEBSDK/20220805 Mobile Safari/537.36 MMWEBID/9538 MicroMessenger/8.0.27.2220(0x28001B53) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 8 Pro Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/045913 Mobile Safari/537.36 V1_AND_SQ_8.8.68_2538_YYB_D A_8086800 QQ/8.8.68.7265 NetType/WIFI WebP/0.3.0 Pixel/1080 StatusBarHeight/76 SimpleUISwitch/1 QQTheme/2971 InMagicWin/0 StudyMode/0 CurrentMode/1 CurrentFontScale/1.0 GlobalDensityScale/0.9818182 AppId/537112567 Edg/98.0.4758.102",
]

driver_path = r"C:\Users\11575\Downloads\chromedriver-win64\chromedriver.exe"
