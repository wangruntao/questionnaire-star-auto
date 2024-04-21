import platform
import subprocess
import os


def kill_chrome():
    try:
        # 检查操作系统
        if platform.system() == "Windows":
            os.system("taskkill /f /im chrome.exe")
            os.system("taskkill /f /im chromedriver.exe")
        elif platform.system() == "Darwin":  # macOS
            os.system("pkill Chrome")
            os.system("pkill chromedriver")
        else:  # Linux 或类Unix系统
            os.system("pkill -f chrome")
            os.system("pkill -f chromedriver")
    except Exception as e:
        print(f"An error occurred while killing Chrome processes: {e}")


# 定时执行kill_chrome函数
import threading


def kill_chrome_periodically(interval):
    kill_chrome()
    # 重新设置定时器以持续定期执行
    threading.Timer(interval, kill_chrome_periodically, [interval]).start()

if __name__ == '__main__':
    # 例如，每10分钟杀死一次Chrome进程
    kill_chrome_periodically(600)  # interval 单位是秒
