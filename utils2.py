import collections
import random
import time
import numpy as np
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import numpy
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import preprocess_prob, add_one


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
        submit_button = driver.find_element(By.XPATH, '//*[@id="ctlNext"]')
        submit_button.click()
        # 使用WebDriverWait来等待按钮不可见，表明已经处理完毕
        try:
            WebDriverWait(driver, 3).until_not(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="ctlNext"]'))
            )
            print("Button is no longer visible, assumed success.")
            return True
        except TimeoutException:
            # 如果等待超时，则认为按钮仍然可见，可能是提交未成功
            print("需要验证")

    except Exception as e:
        print('点击失败')
    # 请点击智能验证码进行验证！
    try:
        comfirm = driver.find_element(By.XPATH, '//*[@id="layui-layer1"]/div[3]/a')
        comfirm.click()
        time.sleep(1)
        print('验证成功')
    except Exception as e:
        pass
        # print(e)

    flag = False
    # 点击按钮开始智能验证
    try:
        button = driver.find_element(By.XPATH, '//*[@id="SM_BTN_WRAPPER_1"]')
        button.click()
        time.sleep(0.5)
        flag = True
        print('验证成功')
    except Exception as e:
        pass
        # print(e)

    # 滑块验证
    try:
        slider = driver.find_element(By.XPATH, '//*[@id="nc_1__scale_text"]/span')
        time.sleep(0.3)
        if str(slider.text).startswith("请按住滑块，拖动到最右边"):
            width = slider.size.get('width')
            ActionChains(driver).drag_and_drop_by_offset(slider, width, 0).perform()
            time.sleep(1)
            flag = True
            print('验证成功')
    except Exception as e:
        pass
        # print(e)

    time.sleep(3)
    driver.quit()

    return flag


# type = 3 单选
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


# type = 6
def matrix_scale2(driver, id, prob):
    xpath = '//*[@id="divRefTab{}"]/tbody/tr'.format(id)
    q_len = (len(driver.find_elements(By.XPATH, xpath)) - 1) / 2
    last_choices = collections.deque(maxlen=3)  # 使用双端队列存储最近的两个选择
    for i in range(1, int(q_len) + 1):
        xpath = '//*[@id="drv{}_{}"]/td'.format(id, i)
        answers = driver.find_elements(By.XPATH, xpath)
        p = preprocess_prob(prob.get(id), len(answers) - 1)
        choice = numpy.random.choice(a=numpy.arange(1, len(answers)), p=p)
        while len(last_choices) == 3 and last_choices.count(choice) == 3:
            choice = np.random.choice(a=np.arange(1, len(answers)), p=p)
        last_choices.append(choice)  # 更新选择历史
        xpath = '//*[@id="drv{}_{}"]/td[{}]'.format(id, i, choice + 1)
        time.sleep(random.uniform(0, 1))
        driver.find_element(By.XPATH, xpath).click()


# type =1
def fill_single_blank2(driver, id, prob):
    # 构建 XPath，用于定位对应的输入框
    xpath = f'//*[@id="div{id}"]//input[@type="text"]'

    # 从对应题目的答案列表中随机选择一个答案
    try:
        num = random.randint(0, len(prob.get(id)) - 1)
        text = prob.get(id)[num]
    except:
        text = "无"

    # 定位到输入框并发送选中的答案文本
    input_element = driver.find_element(By.XPATH, xpath)
    input_element.send_keys(text)


# 简答题 type=2
def fill_blank2(driver, id, answerList):
    xpath = '//*[@id="div{}"]/div[2]/textarea'.format(id)
    # text = select_answer(answerList)

    try:
        num = random.randint(0, len(answerList.get(id)) - 1)
        text = answerList.get(id)[num]
    except:
        text = "无"
    driver.find_element(By.XPATH, xpath).send_keys(text)


# 矩阵填空，type=9
def matrix_fill_blank2(driver, id, prob, idx):
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


# 下拉框 type=7
def select2(driver, id, prob):
    xpath = '//*[@id="div{}"]/div[2]'.format(id)
    driver.find_element(By.XPATH, xpath).click()
    xpath = "//*[@id='select2-q{}-results']/li".format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    # 有一个“请选择”,所以len-1
    p = preprocess_prob(prob.get(id), len(answers) - 1)
    choice = numpy.random.choice(a=numpy.arange(1, len(answers)), p=p)
    xpath = "//*[@id='select2-q{}-results']/li[{}]".format(id, choice + 1)
    driver.find_element(By.XPATH, xpath).click()


# type = 5
def single_scale2(driver, id, prob):
    xpath = '//*[@id="div{}"]/div[2]/div/ul/li'.format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    p = preprocess_prob(prob.get(id), len(answers))
    choice = numpy.random.choice(a=numpy.arange(1, len(answers) + 1), p=p)
    xpath = '//*[@id="div{}"]/div[2]/div/ul/li[{}]'.format(id, choice)
    driver.find_element(By.XPATH, xpath).click()


# 排序题 type = 11
def sort2(driver, id, prob):
    xpath = '//*[@id="div{}"]/ul/li'.format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    # TODO 默认排序
    try:
        order = prob.get(id)[:]
    except:
        order = [i+1 for i in range(len(answers))]
    for i in range(len(order)):
        index = order[i]
        xpath = '//*[@id="div{}"]/ul/li[{}]'.format(id, index)
        driver.find_element(By.XPATH, xpath).click()
        time.sleep(0.5)
        order = add_one(order, index, i)
