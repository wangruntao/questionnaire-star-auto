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
def detect_full1(driver):
    try:
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//div[text()='系统提示']")))
        return True
    except (NoSuchElementException, TimeoutException):
        return False


def click_button1(driver):
    # driver.get(r'https://www.wjx.cn/vj/wk8Yo2t.aspx')

    try:
        submit_button = driver.find_element(By.ID, "submit_button")
        submit_button.click()
        if not detect_full1(driver):  # Check if the "系统提示" is not there
            print(f"System prompt not found.")
        else:
            print("Survey completed and system prompt detected.")
            return False

    finally:
        pass
        # driver.quit()
    return True


def single_choice1(driver, id, prob):
    xpath = '//*[@id="div{}"]/div[2]/ul/li'.format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    p = preprocess_prob(prob.get(id), len(answers))
    choice = numpy.random.choice(a=numpy.arange(1, len(answers) + 1), p=p)
    xpath = '//*[@id="div{}"]/div[2]/ul/li[{}]'.format(id, choice)
    target_element = driver.find_element(By.XPATH, xpath)
    ActionChains(driver).move_to_element(target_element).click().perform()


# 多选 type=4
def multi_choice1(driver, id, prob):
    xpath = f'//*[@id="div{id}"]/div[2]/ul/li'
    answers = driver.find_elements(By.XPATH, xpath)
    p = preprocess_prob(prob.get(id), len(answers))
    # 过滤掉概率为0的选项
    options = [i + 1 for i, x in enumerate(p) if x > 0]
    p_filtered = [x for x in p if x > 0]
    if not options:
        return  # 如果没有有效选项，退出函数
        # 确定随机选择的数量
    n = random.randint(1, len(options))
    q_selects = np.random.choice(a=options, size=n, replace=False, p=p_filtered)

    for j in q_selects:
        checkbox_xpath = f'//*[@id="div{id}"]/div[2]/ul/li[{j}]/a'
        WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, checkbox_xpath))
        )
        driver.find_element(By.XPATH, checkbox_xpath).click()
