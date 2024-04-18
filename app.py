import json
import multiprocessing
import random
import threading
from concurrent.futures import ThreadPoolExecutor
import time
from utils import get_url_content
from stream_line import survey_thread
from src.chrom import setup_driver
import config
from flask import Flask, request, jsonify
import threading
from concurrent.futures import ThreadPoolExecutor
import time

task_list = []
app = Flask(__name__)


@app.route('/update_task_list', methods=['POST'])
def update_task_list():
    global task_list
    new_task_list = request.json.get('task_list')
    task_list.extend(new_task_list)
    print("Task list updated successfully.")
    return "Task list updated successfully."


def execute_tasks():
    while True:
        if task_list:
            task_json = task_list.pop(0)
            if task_json.strip():  # 检查任务字符串是否为空或只包含空白字符
                task = json.loads(task_json)
                url = task.get('url')
                num = task.get('num')
                prob = task.get('prob')
                type_of_question = get_url_content(url)
                count_lock = threading.Lock()
                count = multiprocessing.Value('i', 0)
                with ThreadPoolExecutor(max_workers=config.thread_num) as executor:
                    for _ in range(config.thread_num):
                        executor.submit(survey_thread, url, num, prob, type_of_question, count_lock, count)
            else:
                print("Invalid task format, skipping...")
        else:
            print("No tasks in the list, waiting for new tasks...")
            time.sleep(5)


if __name__ == "__main__":
    threading.Thread(target=execute_tasks).start()
    app.run(debug=True)