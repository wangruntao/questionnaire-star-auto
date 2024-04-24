import json
import random
import time
import uuid

import redis
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import numpy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

redis_client = redis.Redis(host='localhost', port=6379, db=0)


def increment_num(num):
    redis_client.incrby('survey_count', num)


def decrement_num(num):
    # 减少问卷数量
    redis_client.decrby('survey_count', num)


def add_task(url, prob, num):
    task_id = str(uuid.uuid4())
    task_data = {
        'url': url,
        'prob': json.dumps(prob),
        'num': num
    }

    # redis_client.hmset(f"task:{task_id}", task_data)
    for key, value in task_data.items():
        redis_client.hset(f"task:{task_id}", key, value)

    # redis_client.lpush('taskqueue', task_id)
    # Check the type of 'task_queue'
    if redis_client.type('task_queue').decode('utf-8') != 'list':
        print("Resetting 'task_queue'...")
        redis_client.delete('task_queue')  # This will delete the key if it's not a list.

    # Now you can safely use 'task_queue' as a list
    redis_client.lpush('task_queue', task_id)  # Example of adding an item to the list

    increment_num(num)
    return task_id


def get_que_and_ans(url):
    # Configure ChromeOptions
    options = Options()
    options.add_argument('--headless')

    driver = webdriver.Chrome(options)  # or whichever browser driver you need
    driver.get(url)

    html_content = driver.page_source

    # Process HTML content to get question mapping


def get_url_content(url):
    # Configure ChromeOptions
    options = Options()
    options.add_argument('--headless')

    driver = webdriver.Chrome(options)  # or whichever browser driver you need
    driver.get(url)

    html_content = driver.page_source
    # print(html_content)
    driver.quit()
    # Process HTML content to get question mapping
    if html_content:
        question_type_mapping = map_questions_to_types(html_content)
        print("答案类型为：", question_type_mapping)
        return question_type_mapping
    else:
        print("Failed to retrieve HTML content from the URL.")


def map_questions_to_types(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    type_of_question = {i: [] for i in range(1, 21)}  # Adjust range as necessary

    question_divs = soup.find_all('div', {'data-role': 'fieldcontain'})

    for div in question_divs:
        topic = div.get('topic')
        question_type = div.get('type')
        if topic and question_type:
            topic_number = int(topic)
            question_type = int(question_type)
            type_of_question[question_type].append(topic_number)

    return type_of_question


# 选取答案
def select_answer(answerList):
    length = len(answerList)
    index = random.randint(0, length - 1)
    return answerList[index]


# 简答题题 type=2
def fill_blank(driver, id, answerList, idx):
    xpath = '//*[@id="div{}"]/div[2]/textarea'.format(id)
    # text = select_answer(answerList)
    num = random.randint(0, len(answerList.get(idx)) - 1)
    text = answerList.get(idx)[num]
    driver.find_element(By.XPATH, xpath).send_keys(text)
    idx += 1
    return idx


# 归一化比例
def preprocess_prob(probabilities, total_options):
    if probabilities is None:
        # 如果没有提供概率，则均等分配
        return [1 / total_options] * total_options
    elif sum(probabilities) == 0:
        # 如果所有概率都是0，则均等分配
        return [1 / total_options] * total_options
    else:
        # 正常归一化概率
        prob_sum = sum(probabilities)
        return [p / prob_sum for p in probabilities]


# 单量表题 type=5
def single_scale(driver, id, prob, idx):
    xpath = '//*[@id="div{}"]/div[2]/div/ul/li'.format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    p = preprocess_prob(prob.get(idx), len(answers))
    choice = numpy.random.choice(a=numpy.arange(1, len(answers) + 1), p=p)
    xpath = '//*[@id="div{}"]/div[2]/div/ul/li[{}]'.format(id, choice)
    driver.find_element(By.XPATH, xpath).click()
    idx += 1
    return idx


# 矩阵量表 type=6
# 单选
def single_matrix_scale(driver, id, prob, idx, num):
    xpath = '//*[@id="divRefTab{}"]/tbody/tr'.format(id)
    q_len = (len(driver.find_elements(By.XPATH, xpath)) - 1) / 2
    for i in range(1, int(q_len) + 1):
        xpath = '//*[@id="drv{}_{}"]/td'.format(id, i)
        answers = driver.find_elements(By.XPATH, xpath)
        # 判断是浏览器还是QQ、微信
        if num == 0:
            p = preprocess_prob(prob.get(idx), len(answers) - 1)
            choice = numpy.random.choice(a=numpy.arange(1, len(answers)), p=p)
        else:
            p = preprocess_prob(prob.get(idx), len(answers))
            choice = numpy.random.choice(a=numpy.arange(0, len(answers)), p=p)
        xpath = '//*[@id="drv{}_{}"]/td[{}]'.format(id, i, choice + 1)
        time.sleep(0.5)
        driver.find_element(By.XPATH, xpath).click()
        idx += 1
    return idx


# 多选
def multi_matrix_scale(driver, id, prob, idx, num):
    xpath = '//*[@id="divRefTab{}"]/tbody/tr'.format(id)
    q_len = (len(driver.find_elements(By.XPATH, xpath)) - 1) / 2
    for i in range(1, int(q_len) + 1):
        xpath = '//*[@id="drv{}_{}"]/td'.format(id, i)
        answers = driver.find_elements(By.XPATH, xpath)
        # 判断是浏览器还是QQ、微信
        if num == 0:
            p = preprocess_prob(prob.get(idx), len(answers) - 1)
            # 多选的数量
            # 概率为0的选项个数
            count = sum(1 for i in p if i == 0)
            n = random.randint(1, len(answers) - 1 - count)
            q_selects = numpy.random.choice(a=numpy.arange(1, len(answers)), size=n, replace=False, p=p)
        else:
            p = preprocess_prob(prob.get(idx), len(answers))
            # 多选的数量
            # 概率为0的选项个数
            count = sum(1 for i in p if i == 0)
            n = random.randint(1, len(answers) - count)
            q_selects = numpy.random.choice(a=numpy.arange(0, len(answers)), size=n, replace=False, p=p)

        for q_select in q_selects:
            xpath = '//*[@id="drv{}_{}"]/td[{}]'.format(id, i, q_select + 1)
            driver.find_element(By.XPATH, xpath).click()
        idx += 1
    return idx


# 滑动条 type=8
def single_slide(driver, id, prob, idx):
    xpath = '//*[@id="jsrs_q{}"]/div[3]/div'.format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    p = preprocess_prob(prob.get(idx), len(answers) - 1)
    choice = numpy.random.choice(a=numpy.arange(0, len(answers) - 1), p=p)
    score = choice * 100 / len(answers) + random.uniform(0, 100 / len(answers))
    text = score * 614 / 100 + 10
    xpath = '//*[@id="jsrs_q{}"]/div[1]'.format(id)
    element = driver.find_element(By.XPATH, xpath)
    ActionChains(driver).move_to_element_with_offset(element, text, 0).click().perform()
    idx += 1
    return idx


# 多滑条 type=9
def multi_slide(driver, id, prob, idx):
    xpath = '//*[@id="divRefTab{}"]/tbody/tr'.format(id)
    q_len = len(driver.find_elements(By.XPATH, xpath)) / 2
    for i in range(0, int(q_len)):
        xpath = '//*[@id="jsrs_q{}_{}"]/div[3]/div'.format(id, i)
        answers = driver.find_elements(By.XPATH, xpath)
        p = preprocess_prob(prob.get(idx), len(answers) - 1)
        choice = numpy.random.choice(a=numpy.arange(0, len(answers) - 1), p=p)
        score = choice * 100 / len(answers) + random.uniform(0, 100 / len(answers))
        text = score * 614 / 100 + 10
        xpath = '//*[@id="jsrs_q{}_{}"]/div[1]'.format(id, i)
        element = driver.find_element(By.XPATH, xpath)
        ActionChains(driver).move_to_element_with_offset(element, text, 0).click().perform()
        idx += 1
    return idx


def add_one(lists, num, index):
    for i in range(index, len(lists)):
        if lists[i] < num:
            lists[i] += 1
    return lists


# 分配题 type=12  暂时还没有完成
def distribute(driver, id, prob, idx):
    xpath = '//*[@id="divRefTab{}"]/tbody/tr'.format(id)
    q_len = len(driver.find_elements(By.XPATH, xpath)) / 2
    for i in range(0, int(q_len)):
        xpath = '//*[@id="jsrs_q{}_{}"]/div[3]/div'.format(id, i)
        answers = driver.find_elements(By.XPATH, xpath)
        p = preprocess_prob(prob.get(idx), len(answers) - 1)
        choice = numpy.random.choice(a=numpy.arange(0, len(answers) - 1), p=p)
        score = choice * 100 / len(answers) + random.uniform(0, 100 / len(answers))
        text = score * 614 / 100 + 10
        xpath = '//*[@id="jsrs_q{}_{}"]/div[1]'.format(id, i)
        element = driver.find_element(By.XPATH, xpath)
        ActionChains(driver).move_to_element_with_offset(element, text, 0).click().perform()
        idx += 1
    return idx
