import os
import json
import threading
import time

from urllib.request import urlopen
def appDownload(url,save_path):
    file_path = save_path + ".tmp"
    try:
        u = urlopen(url)
        with open(file_path, 'wb') as f:
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                f.write(buffer)
        os.rename(file_path,save_path)
        return True
    except Exception as e:
        print("线程名：{}, 下载出现问题".format(threading.current_thread().name, e))
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(save_path):
            os.remove(save_path)
        return False


def download(json_path, apk_save_dir):
    with open(json_path, mode='r') as f:
        apps_json = json.load(f)
    cat = apps_json[0]['cat']
    print("种类：", cat)
    save_dir = apk_save_dir + cat
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    else:  # 如果不限制同类别下载，可以注释该部分代码，有可能造成，一个文件夹（一个类别）的APK数量超过设定的300
        print("发现类别:{0}，同类别重复下载，取消该json文件的下载：{1}".format(cat, json_path))
        return
    num = 0
    for index, item in enumerate(apps_json):
        if num == 300:  # 每个种类只下载300个
            print("线程名：{}, 当前下载结束。。。".format(threading.current_thread().name))
            break
        save_path = os.path.join(save_dir, item['name'] + ".apk")
        if verify_size(item['size']):
            print("线程名：{}, 序号：{},名字：{}<100M，进行下载。。。".format(threading.current_thread().name, num, item['name']))
            if os.path.exists(save_path):
                num = num + 1
                print("已经存在的文件。。。,",save_path)
            else:
                start = time.time()
                flag = appDownload(item['download'], save_path)
                if flag:
                    num = num + 1
                    print("线程名：{}, 下载用时：{}秒".format(threading.current_thread().name, round(time.time() - start),3))
        else:
            print("线程名：{}, 序号：{},名字：{}>100M.....,取消下载。".format(threading.current_thread().name, num, item['name']))

#检测大小，K，M，G
def verify_size(str_size:str, limit_size:int = 100) -> bool:
    if str_size[-1].lower() == 'k':
        size = float(str_size[:-1]) // 1024
        if size < limit_size:
            return True
        else:
            return False
    elif str_size[-1].lower() == 'm':
        size = float(str_size[:-1])
        if size < limit_size:
            return True
        else:
            return False
    elif str_size[-1].lower() == 'g':
        size = float(str_size[:-1]) * 1024
        if size < limit_size:
            return True
        else:
            return False


if __name__ == "__main__":
    json_dir = os.path.abspath(r"./json")  # 下载链接所在目录
    # apk_save_dir = os.path.abspath(r"./app")  # 下载app所在目录，默认当前工程
    apk_save_dir = r"F:\DATABASE\APP"
    json_file_names = os.listdir(json_dir)
    jsons_path = [os.path.join(json_dir, json_name) for json_name in json_file_names]
    path = jsons_path[0]
    threads = list()
    for index, item in enumerate(jsons_path):  # 一个文件（一个种类）设置一个下载线程
        t = threading.Thread(target=download, args=(item, apk_save_dir, ), name="thread" + str(index))
        threads.append(t)
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()
    print("主程序结束！！！")





