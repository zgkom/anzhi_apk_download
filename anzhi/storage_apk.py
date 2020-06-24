import sys
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.config import Config
from utils.mysql import MySQLUtils
from utils.mylog import MyLogging
from anzhi.tools import *


def apk_crawling(json_path, apk_save_dir, download_pool: ThreadPoolExecutor, download_batch=10,
                 limit_download=400, download_limit_size=100):
    with open(json_path, mode='r') as f:
        apps_json = json.load(f)
    cat = apps_json[0]['cat']
    print("种类:", cat)
    save_cat_dir = os.path.join(apk_save_dir, cat)
    if not os.path.exists(save_cat_dir):
        os.makedirs(save_cat_dir)
    task_running = list()  # 记录任务状态
    task_params = list()  #
    task_results = list()
    num = 0
    for index, apk_link_item in enumerate(apps_json):
        if num >= limit_download:  # 每个种类只下载300个
            print("达到限定下载数量，线程名：{}, 当前下载结束...".format(threading.current_thread().name))
            break
        if verify_size(apk_link_item['size'], download_limit_size):
            save_path = os.path.join(save_cat_dir, apk_link_item['name'].replace(" ", "") + ".apk")  # 将APK名字中的空格除去
            if os.path.exists(save_path):
                print("已经存在的文件...", save_path)
                continue

            # 将下载链接和保存位置提交给线程池
            num += 1
            param = {"apk_link_info": apk_link_item, "save_path": save_path, "apk_save_dir": apk_save_dir}
            print("下载序号:{0}, 名字:{1}, 添加到下载任务列表...".format(index, apk_link_item['name']))
            task_params.append(param)
            if len(task_params) >= download_batch:
                for param_item in task_params:
                    future = download_pool.submit(crawling_one_apk, **param_item)
                    task_running.append(future)
                    # future.add_done_callback(insert_data)
                # 等待所有任务完成继续
                for future in as_completed(task_running):
                    result = future.result()
                    task_results.append(result)
                insert_batch_data(task_results)
                task_running.clear()  # 内存清空级别
                task_params.clear()
                task_results.clear()

        else:
            print("下载序号:{},名字:{}>100M.....,取消下载。".format(index,apk_link_item['name']))
    if task_params:  # 说明所有可用链接数循环完毕不到limit_download，不到一个提交任务批次
        for param_item in task_params:
            feature = download_pool.submit(crawling_one_apk, **param_item)
            task_running.append(feature)
            # feature.add_done_callback(insert_data)
        # 等待所有任务完成继续
        for future in as_completed(task_running):
            result = future.result()
            task_results.append(result)
        insert_batch_data(task_results)
        task_running.clear()  # 内存清空级别
        task_params.clear()
        task_results.clear()


def crawling_one_apk(apk_link_info, save_path, apk_save_dir=None):
    start = time.time()
    flag = download_one_apk(apk_link_info['download'], save_path)
    if flag:
        hash = acc_md5_hash(save_path)
        print("线程名：{}, apk下载用时：{}秒, 保存路径:{}".format(threading.current_thread().name, round(time.time() - start), 3), save_path)
        # apk入库信息
        apk_insert_info = {
            "name": apk_link_info["name"],
            "hash": hash,
            "category": apk_link_info["cat"],
            "download_cnt": apk_link_info["download_cnt"],
            "release_date": apk_link_info["time"],
            "size": apk_link_info["size"],
            "sys": apk_link_info["sys"],
            "download_url": apk_link_info["download"],
            "path": None
        }
        if apk_save_dir is None:
            apk_insert_info["path"] = save_path
        else:
            related_path = save_path.split(apk_save_dir)[-1]
            apk_insert_info["path"] = related_path.replace("\\", "/")
        return apk_insert_info
    return None


# 回调函数，将下载的apk插入数据库
def insert_batch_data(batch_data):
    global mysql_obj
    sqls = list()
    for data in batch_data:
        if data is not None:
            sql = ("INSERT INTO `apk_manage`.`apk` "
                   "(`name`, `hash`, `category`, `download_cnt`, `release_date`, `size`, `sys`, `download_url`, `path`)"
                   " VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}');".format(
                data['name'], data['hash'], data['category'], data['download_cnt'], data['release_date'],
                data['size'], data['sys'], data['download_url'], data['path']
            ))
            sqls.append(sql)
    # print("插入数据到数据库:{0}".format(feature.result()))
    mysql_obj.batch_insert(sqls)
    print("批量插入数据到数据库成功!!!")

if __name__ == "__main__":
    # 获取当前路径
    this_dir = sys.path[0]
    config_path = os.path.join(this_dir, "../config/params.ini")
    config_obj = Config(config_file_path=config_path)
    log_path = os.path.join(this_dir, "../log/log.txt")
    log_obj = MyLogging(log_path=log_path)
    db_params = config_obj.get_dict_by_section("DB")
    mysql_params = {
        "host": db_params["host"],
        "user_name": db_params["user_name"],
        "user_pwd": db_params["user_pwd"],
        "db_name": db_params["db_name"],
        "db_port": db_params["db_port"],
        "log_obj": log_obj
    }
    mysql_obj = MySQLUtils(**mysql_params)

    # 创建线程池
    thread_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="download_thread_")
    max_works = 300
    path_dict = config_obj.get_dict_by_section("PATH")
    apk_link_dir = r"" + path_dict["apk_link_dir"]
    apk_save_dir = r"" + path_dict["apk_save_dir"]
    json_files = os.listdir(apk_link_dir)
    for json_file in json_files:
        json_link_path = os.path.join(apk_link_dir, json_file)
        apk_crawling(json_link_path, apk_save_dir, thread_pool, limit_download=max_works)


