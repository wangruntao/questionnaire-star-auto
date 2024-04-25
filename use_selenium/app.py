import json
import multiprocessing
import threading
import time
import uuid
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from queue import Queue, Empty

import redis
from flask import Flask, request, jsonify
from flask import Response

import config
from stream_line import survey_thread
from use_selenium.util.pub_utils import get_url_content
from util.get_ques_and_ans import get_que_and_ans
from util.kill_chrom import kill_chrome_periodically

from util.pub_utils import redis_client, add_task, increment_num, decrement_num

# 定义不同状态的任务队列
pending_tasks_queue = Queue()  # 待处理任务队列
paused_tasks_queue = Queue()  # 已暂停任务队列
in_progress_tasks = {}  # 用字典跟踪正在进行的任务
completed_tasks_queue = Queue()  # 已完成任务队列
current_task_id = None
# 用于同步访问正在进行任务的锁
tasks_lock = threading.Lock()

app = Flask(__name__)


@app.route('/get_num', methods=['GET'])
def get_num():
    survey_count = redis_client.get('survey_count')
    if survey_count is None:
        redis_client.set('survey_count', 0)
        survey_count = 0
    else:
        survey_count = int(survey_count)
    return jsonify({'count': survey_count})


@app.route('/record_visit', methods=['GET'])
def record_visit():
    print('Recording visit...')
    redis_client.incr('visit_count')
    return jsonify(success=True)


@app.route('/get_wait_num', methods=['GET'])
def get_wait_num():
    wait = pending_tasks_queue.qsize()
    return jsonify(wait=int(wait))


@app.route('/get_visits', methods=['GET'])
def get_visits():
    print('get_visit')
    visits = redis_client.get('visit_count') or 0
    return jsonify(visits=int(visits))


@app.route('/handle_task', methods=['POST'])
def handle_task():
    # 尝试获取JSON数据
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No JSON data provided"}), 400

    # 从JSON数据中提取url和prob
    url = data.get('url')
    prob = data.get('prob')
    if not url or not prob:
        return jsonify({"status": "error", "message": "Missing 'url' or 'prob' field"}), 400

    # 你的处理逻辑...
    print(f"Handling task with url: {url} and prob: {prob}")

    # 假设处理成功，返回成功的响应
    return jsonify({"status": "success", "message": "Task handled successfully"})


@app.route('/get_tasks_by_url', methods=['GET'])
def get_tasks_by_url():
    url_id = request.args.get('url_id')
    print(url_id)
    if not url_id:
        return jsonify({"error": "URL ID parameter is missing"}), 400

    task_ids = redis_client.lrange(f"url_to_task_id:{url_id}", 0, -1)
    if not task_ids:
        return jsonify({"error": "No tasks associated with the given URL ID"}), 404

    task_ids = [tid.decode('utf-8') for tid in task_ids]
    return jsonify({"task_ids": task_ids}), 200




@app.route('/analyze', methods=['POST'])
def analyze_url():
    data = request.get_json()
    url = data['url']
    results = get_que_and_ans(url)
    return Response(results, mimetype='application/json')


# 增加任务
@app.route('/update_task_list', methods=['POST'])
def update_task_list():
    data = request.json.get('task_list')
    # Generate a unique task ID
    task_id = add_task(data['url'], data['prob'], data['num'])
    print(f"Task list updated successfully with task ID {task_id}.")
    return jsonify({"message": "Task list updated successfully.", "task_id": task_id}), 200


@app.route('/start_task/', methods=['POST'])
def start_task():
    task_id = request.json.get('task_id')
    print(task_id)
    # 从Redis获取任务详情
    task_data = redis_client.hgetall(f"task:{task_id}")
    if not task_data:
        return jsonify({"error": "Task not found"}), 404

    # 将从Redis获取的数据（字节字符串）转换为正常的字符串
    task = {key.decode('utf-8'): value.decode('utf-8') for key, value in task_data.items()}

    # 将prob字段（如果存在）从字符串转换回字典
    if 'prob' in task:
        try:
            task['prob'] = json.loads(task['prob'])
        except json.JSONDecodeError:
            return jsonify({"error": "Failed to decode the 'prob' field"}), 500

    # 将任务放入待处理队列
    pending_tasks_queue.put(task)

    return jsonify({"message": "Task started successfully", "task_id": task_id}), 200


def execute_tasks():
    while True:
        try:
            task = pending_tasks_queue.get(timeout=5)
            if not task:
                print("No task  retrieved from the queue")
                continue

            print(f"Current task set to {task}")
            # 更多的任务处理逻辑...
            process_task(task)
        except Empty:
            print("No tasks in the queue, waiting for new tasks...")
        except Exception as e:
            print(f"Error processing task: {str(e)}")


def process_task(task):
    # 获取任务详情
    start_time = time.time()
    url = task.get('url')
    num = int(task.get('num'))
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
    increment_num(num)

    # 使用线程池来并发执行任务
    with ThreadPoolExecutor(max_workers=config.thread_num) as executor:
        futures = [executor.submit(survey_thread, url, num, prob_with_int_keys, type_of_question, count_lock, count)
                   for _ in range(config.thread_num)]
        # 等待所有线程完成任务
        for future in as_completed(futures):
            try:
                result = future.result()
            except Exception as exc:
                print(f"A task failed with exception: {exc}")
            else:
                print(f"Task completed successfully: {result}")
    # 打印任务完成信息
    print(f"Task for URL: {url} completed.")
    end_time = time.time()
    decrement_num(num)
    print(f"用时: {end_time - start_time:.2f}秒")


if __name__ == "__main__":
    # 开启时默认无任务
    redis_client.setnx('survey_count', 0)
    # threading.Thread(target=kill_chrome_periodically, daemon=True, args=(config.kill_chrome_interval,)).start()
    threading.Thread(target=execute_tasks, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
