import random
import time
import numpy as np
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import numpy
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import preprocess_prob


# 检查有没有答完
def detect_full2(driver):
    try:
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//div[text()='系统提示']")))
        return True
    except (NoSuchElementException, TimeoutException):
        return False


def click_button2(driver):
    # driver.get(r'https://www.wjx.cn/vj/wk8Yo2t.aspx')

    try:
        submit_button = driver.find_element(By.ID, "ctlNext")
        submit_button.click()
        if not detect_full2(driver):  # Check if the "系统提示" is not there
            print(f"System prompt not found.")
        else:
            print("Survey completed and system prompt detected.")
            return False

    finally:
        pass
        # driver.quit()
    return True


def single_choice2(driver, id, prob):
    xpath = '//*[@id="div{}"]/div[2]/div'.format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    # 如果没有传入比例，默认为等比例
    p = preprocess_prob(prob.get(id), len(answers))
    choice = numpy.random.choice(a=numpy.arange(len(answers)), p=p)
    xpath = '//*[@id="div{}"]/div[2]/div[{}]'.format(id, choice + 1)
    # driver.find_element(By.XPATH, xpath).click()
    ActionChains(driver).move_to_element(driver.find_element(By.XPATH, xpath)).click().perform()


# 多选 type=4
def multi_choice2(driver, id, prob):
    xpath = '//*[@id="div{}"]/div[2]/div'.format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    p = preprocess_prob(prob.get(id), len(answers))
    # 多选的数量
    # 概率为0的选项个数
    count = sum(1 for i in p if i == 0)
    n = random.randint(1, len(answers) - count)
    q_selects = numpy.random.choice(a=numpy.arange(1, len(answers) + 1), size=n, replace=False, p=p)
    for j in q_selects:
        driver.find_element(By.XPATH, '//*[@id="div{}"]/div[2]/div[{}]'.format(id, j)).click()
