from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json

question_types = {
    3: "单选题",
    4: "多选题",
    1: "填空题",
    2: "问答题",
    5: "量表题",
    6: "矩阵量表题",
    7: "下拉框题",
    11: "排序题",
    # 根据你的实际需要添加其他类型
    # 比如：type编号: "题目类型描述"
    # type编号要和HTML元素上的type属性值相匹配
}


def get_que_and_ans(url):
    # Configure WebDriver to run headless
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all question divs
    questions = soup.find_all('div', class_='field ui-field-contain')

    # Prepare a list to hold question and answer data
    que_ans_data = []
    count = 1
    for question in questions:
        # Extract the question text
        question_text = question.find('div', class_='topichtml').text.strip()

        # Initialize the answer count
        answer_count = 0

        # Check for different types of questions and count the answers/options
        if question.get('type') == '3':  # Single choice
            answer_count = len(question.find_all('input', type='radio'))
        elif question.get('type') == '4':  # Multiple choice
            answer_count = len(question.find_all('input', type='checkbox'))
        elif question.get('type') == '7':  # Dropdown
            answer_count = len(question.find_all('option')) - 1  # Exclude 'Please select'
        elif question.get('type') == '5':  # Scale
            answer_count = len(question.find_all('a', class_='rate-off'))
        elif question.get('type') == '6':  # Matrix scale
            table = question.find('table', class_='matrix-rating matrixtable')
            rows = table.find_all('tr')
            # 计算第一行中所有单选按钮的数量
            # 第一行评分选项（通常是第二行TR元素）
            if len(rows) > 0:
                first_row = rows[-1]
                # 计算评分选项的数量
                answer_count = len(first_row.find_all('a', class_='rate-off rate-offlarge'))



        # Add more conditions for different types if necessary

        # Append the question and answer data to the list
        que_ans_data.append({
            'questionNumber': count,
            'type': question_types.get(int(question.get('type'))),
            'question': question_text,
            'answer_count': answer_count
        })
        count += 1

    driver.quit()  # Make sure to close the driver

    # Convert the list to JSON
    return json.dumps(que_ans_data, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    # Test the function
    url = "https://www.wjx.cn/vm/QN6L2lI.aspx#"
    print(get_que_and_ans(url))
