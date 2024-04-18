import json
import multiprocessing
from concurrent.futures.thread import ThreadPoolExecutor
import config
from flask import Flask, request, jsonify
import threading
import time
from stream_line import survey_thread
from utils import get_url_content
from queue import Queue, Empty
import threading
import uuid
# 定义不同状态的任务队列
pending_tasks_queue = Queue()  # 待处理任务队列
paused_tasks_queue = Queue()  # 已暂停任务队列
in_progress_tasks = {}  # 用字典跟踪正在进行的任务
completed_tasks_queue = Queue()  # 已完成任务队列

# 用于同步访问正在进行任务的锁
tasks_lock = threading.Lock()

app = Flask(__name__)


@app.route('/update_task_list', methods=['POST'])
def update_task_list():
    task = request.json.get('task_list')
    # Generate a unique task ID
    task_id = str(uuid.uuid4())  # Generate a unique identifier
    task['id'] = task_id  # Attach the unique identifier to the task
    pending_tasks_queue.put(task)  # Add the task to the pending tasks queue
    print(f"Task list updated successfully with task ID {task_id}.")
    return jsonify({"message": "Task list updated successfully.", "task_id": task_id}), 200

@app.route('/pause_task', methods=['POST'])
def pause_task():
    with tasks_lock:
        if in_progress_tasks:
            task_id, task = in_progress_tasks.popitem()
            paused_tasks_queue.put(task)
            return jsonify({"message": "Task paused successfully.", "task_id": task_id}), 200
        else:
            return jsonify({"message": "No task is currently in progress."}), 404



def execute_tasks():
    while True:
        try:
            # 尝试从任务队列中获取任务，等待最长5秒
            task = pending_tasks_queue.get(timeout=5)
            task_id = task.get('id')  # 假设每个任务都有一个唯一的标识符
            print("task_id: ", task_id)

            # 使用锁来确保对正在进行任务列表的线程安全操作
            with tasks_lock:
                in_progress_tasks[task_id] = task  # 将任务添加到正在进行的任务字典中

            # 处理任务
            process_task(task)

            # 处理完毕后，从正在进行的任务列表中移除任务，并将其加入已完成任务队列
            with tasks_lock:
                del in_progress_tasks[task_id]
                completed_tasks_queue.put(task)

        except Empty:
            # 如果队列为空，则打印信息并等待新的任务
            print("No tasks in the list, waiting for new tasks...")


def process_task(task):
    # 获取任务详情
    url = task.get('url')
    num = task.get('num')
    prob_str = task.get('prob')
    print(f"Executing task for URL: {url} with num: {num} and prob: {prob_str}")

    try:
        # 尝试解析概率字段，如果是字符串则解析为字典
        prob = json.loads(prob_str) if isinstance(prob_str, str) else prob_str
        # 将概率字典中的键转换为整数类型
        prob_with_int_keys = {int(k): v for k, v in prob.items()}
    except json.JSONDecodeError as e:
        # 如果解析失败，打印错误信息并返回
        print(f"Failed to decode prob: {e}")
        return

    type_of_question = get_url_content(url)

    count_lock = threading.Lock()
    count = multiprocessing.Value('i', 0)

    # 使用线程池来并发执行任务
    with ThreadPoolExecutor(max_workers=config.thread_num) as executor:
        futures = [executor.submit(survey_thread, url, num, prob_with_int_keys, type_of_question, count_lock, count)
                   for _ in range(config.thread_num)]
        # 等待所有线程完成任务
        for future in futures:
            future.result()

    # 打印任务完成信息
    print(f"Task for URL: {url} completed.")


if __name__ == "__main__":
    threading.Thread(target=execute_tasks, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
