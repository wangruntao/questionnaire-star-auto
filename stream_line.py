import threading
import random
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config
from init import setup_driver
import psutil
from utils1 import single_choice1, multi_choice1, click_button1
from utils2 import single_choice2, multi_choice2, click_button2


def open_survey_and_wait(driver, url):
    driver.get(url)
    try:
        # 等待问卷的第一个问题加载完毕，你可以根据你的页面结构调整这里的选择器
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.' + div_name.replace(' ', '.')))
        )
        # print("Page has loaded and questions are visible.")
    except TimeoutException:
        print("Timed out waiting for page to load")
        driver.quit()


#  遍历每一道题
def determine_question_type(driver):
    # 将题号与题型关联
    single_choice_questions = config.single_choice_questions
    multiple_choice_questions = config.multiple_choice_questions

    # 获取所有问题的容器
    questions = driver.find_elements(By.CSS_SELECTOR, '.' + div_name.replace(' ', '.'))
    for question in questions:
        # 获取题号，这里假设题号位于元素的ID中，形式如"div1", "div2"等
        question_id = int(question.get_attribute('id').replace('div', ''))
        # 根据题号判断题型并输出
        if question_id in single_choice_questions:
            # print(f"Question {question_id} is a single-choice question.")
            try:
                single_choice[type](driver, question_id, prob)
            except Exception as e:
                # 打印出错误信息和出错的题号
                print(f"Error answering single-choice question {question_id}: {e}")
                # break
        elif question_id in multiple_choice_questions:
            # print(f"Question {question_id} is a multiple-choice question.")
            try:
                multi_choice[type](driver, question_id, prob)
            except Exception as e:
                pass
                print(f"Error answering multiple-choice question {question_id}:{e}")
        else:
            print(f"Question {question_id} is not clearly categorized.")
        time.sleep(1)


def kill_chromedriver_by_pid(pid):
    try:
        p = psutil.Process(pid)
        if p.is_running():
            p.terminate()  # 尝试正常结束
            p.wait(timeout=5)  # 等待进程结束
            if p.is_running():
                p.kill()  # 强制结束
    except psutil.NoSuchProcess:
        print(f"No process with PID {pid}. It may have already exited.")
    except psutil.AccessDenied:
        print(f"Permission denied to kill process with PID {pid}.")
    except Exception as e:
        print(f"Failed to kill chromedriver with PID {pid}: {e}")


def survey_thread():
    global count
    while True:

        user_agent = random.choice(user_agents)  # 从UA列表中随机选择一个
        driver, pid = setup_driver(user_agent)  # 设置浏览器驱动
        try:
            with count_lock:
                if count >= target_num:
                    driver.quit()  # 确保退出driver
                    break
            open_survey_and_wait(driver, url=url)
            determine_question_type(driver)
            if click_button[type](driver):  # 假设这里返回一个布尔值表示是否继续
                with count_lock:
                    count += 1
                    print(f"count is increased to {count}")

        except Exception as e:
            print(f"Error during survey completion: {str(e)}")
        finally:
            driver.quit()  # 无论如何都确保关闭浏览器
            kill_chromedriver_by_pid(pid)
        time.sleep(sleep_time)


count = 0
count_lock = threading.Lock()
sleep_time = config.sleep_time
api = config.api
prob = config.prob
target_num = config.epoch
single_choice = {
    1: single_choice1,
    2: single_choice2
}
multi_choice = {
    1: multi_choice1,
    2: multi_choice2
}
click_button = {
    1: click_button1,
    2: click_button2
}
type = config.type
div_name = 'div_question' if type == 1 else 'field ui-field-contain'
url = config.url
user_agents = config.UA
# 多线程刷
if __name__ == "__main__":

    # 创建和启动线程
    threads = []
    for _ in range(config.thread_num):  # 创建10个并发线程
        t = threading.Thread(target=survey_thread)
        t.start()
        threads.append(t)

    # 等待所有线程完成
    for t in threads:
        t.join()

    print("All surveys are completed.")
