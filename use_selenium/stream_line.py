import multiprocessing
import threading
import random
import time

import requests
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from urllib3.exceptions import NewConnectionError, MaxRetryError
from use_selenium.util.pub_utils import get_url_content
import config
from init import setup_driver
import psutil
from use_selenium.util.utils1 import single_choice1, multi_choice1, click_button1, matrix_scale1, select1, \
    single_scale1, sort1, \
    fill_blank1, fill_single_blank1
from use_selenium.util.vm_utils import single_choice2, multi_choice2, click_button2, matrix_scale2, select2, \
    single_scale2, sort2, \
    fill_blank2, fill_single_blank2, fill_all_other

#
proxy_lock = threading.Lock()


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
def determine_question_type(driver, prob, type_of_question):
    # 将题号与题型关联
    fill_single_blank_questions = type_of_question.get(1)
    fill_blank_questions = type_of_question.get(2)
    single_choice_questions = type_of_question.get(3)
    multiple_choice_questions = type_of_question.get(4)
    single_scale_questions = type_of_question.get(5)
    matrix_rating = type_of_question.get(6)
    select_questions = type_of_question.get(7)
    sort_questions = type_of_question.get(11)
    # 获取所有问题的容器
    questions = driver.find_elements(By.CSS_SELECTOR, '.' + div_name.replace(' ', '.'))
    for question in questions:
        # 获取题号，这里假设题号位于元素的ID中，形式如"div1", "div2"等
        question_id = int(question.get_attribute('id').replace('div', ''))
        # print(question_id)
        # 根据题号判断题型并输出
        # 如果是单选题3
        if question_id in single_choice_questions:
            # print(f"Question {question_id} is a single-choice question.")
            try:
                single_choice[type](driver, question_id, prob)
            except Exception as e:
                print(f"Question {question_id} is a single-choice question.")
        elif question_id in fill_single_blank_questions:
            try:
                fill_single_blank[type](driver, question_id, prob)
            except Exception as e:
                print(e, f"Question {question_id} ")

        elif question_id in fill_blank_questions:
            try:
                fill_blank[type](driver, question_id, prob)
            except:
                print(f"Question {question_id} ")
        # 如果是多选题4
        elif question_id in multiple_choice_questions:
            try:
                multi_choice[type](driver, question_id, prob)
            except:
                print(f"Question {question_id} ")
            # multi_choice[type](driver, question_id, prob)

        elif question_id in single_scale_questions:
            try:
                single_scale[type](driver, question_id, prob)
            except:
                print(f"Question {question_id} ")
            # single_scale[type](driver, question_id, prob)

        # 如果是q矩阵量表
        elif question_id in matrix_rating:
            try:
                matrix_scale[type](driver, question_id, prob)
            except:
                print(f"Question {question_id} ")
            # matrix_scale[type](driver, question_id, prob)

        # 如果是下拉框
        elif question_id in select_questions:
            try:
                select[type](driver, question_id, prob)
            except Exception as e:
                print(e, f"Question {question_id} ")
            # select[type](driver, question_id, prob)

        elif question_id in sort_questions:
            try:
                sort[type](driver, question_id, prob)
            except Exception as e:
                print(e, f"Question {question_id} ")
            # sort[type](driver, question_id, prob)

        else:
            print(f"Question {question_id} is not clearly categorized.")
        # time.sleep(random.uniform(0, 1))
    fill_all_other(driver)
    time.sleep(random.uniform(0, 2))


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


def updata_proxy_data(api):
    with proxy_lock:
        try:
            response = requests.get(api, timeout=10)
            if response.status_code == 200:
                proxy_data = response.json()
                config.proxy_data = proxy_data
                print("更新代理")
            else:
                print(f"请求失败，状态码：{response.status_code}")
        except requests.RequestException as e:
            print(f"请求过程中发生错误: {e}")


def survey_thread(url, num, prob, type_of_question, count_lock, count):
    while count.value < num:
        user_agent = random.choice(user_agents)
        driver = setup_driver(user_agent)
        try:
            open_survey_and_wait(driver, url=url)
            determine_question_type(driver, prob, type_of_question)
            if click_button[type](driver):
                with count_lock:
                    count.value += 1
                    print(f"完成数量增加到 {count.value}")
                    if count.value % 10 == 0 and config.use_proxy_pool:
                        updata_proxy_data(config.api)
        except NewConnectionError as e:
            print(f"无法建立新连接：{e}")
        except MaxRetryError as e:
            print(f"尝试连接次数超过限制：{e.reason}")
        except WebDriverException as e:
            print(f"WebDriver 异常：{e}")
        except Exception as e:
            print(f"在完成问卷时发生错误：{e}，url：{url}，prob：{prob}")
        finally:
            if driver is not None:
                try:
                    driver.quit()
                    print(f"任务 {url} 的驱动已正确退出。")
                except WebDriverException:
                    print(f"关闭驱动时发生错误，任务 {url}。")
            time.sleep(1)  # 如果你希望在每次循环之间有暂停的话


# 在 main 函数中修改线程创建逻辑
def main():
    for task in config.task_list:
        url = task.get('url')
        num = task.get('num')
        prob = task.get('prob')
        type_of_question = get_url_content(url)
        count_lock = threading.Lock()
        threads = []
        count = multiprocessing.Value('i', 0)  # Initializing count as multiprocessing Value
        for _ in range(config.thread_num):  # 每个任务创建多个线程
            thread = threading.Thread(target=survey_thread, args=(url, num, prob, type_of_question, count_lock, count))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()


sleep_time = config.sleep_time
api = config.api
# prob = config.prob
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
matrix_scale = {
    1: matrix_scale1,
    2: matrix_scale2
}
select = {
    1: select1,
    2: select2
}
single_scale = {
    1: single_scale1,
    2: single_scale2
}
sort = {
    1: sort1,
    2: sort2
}
fill_blank = {
    1: fill_blank1,
    2: fill_blank2
}
fill_single_blank = {
    1: fill_single_blank1,
    2: fill_single_blank2
}
type = config.type
div_name = 'div_question' if type == 1 else 'field ui-field-contain'
url = config.url
user_agents = config.UA

# 多线程刷


if __name__ == "__main__":
    type_of_question = []
    for task in config.task_list:
        url = task.get('url')
        print(url)
        prob = task.get('prob')
        num = task.get('num')
        type_of_question = get_url_content(url)
        count_lock = threading.Lock()
        count = multiprocessing.Value('i', 0)
        survey_thread(url, 10, prob, type_of_question, count_lock, count)
