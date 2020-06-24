"""
用于安智市场APK下载时需要的工具函数
"""
import os
import hashlib
import threading
from urllib.request import urlopen


# 检测大小，K，M，G
def verify_size(str_size: str, limit_size: int = 100) -> bool:
    """
    解析APK大小表示的字符串，默认限定100M以下
    :param str_size: APK大小字符串，例如100K，2M，1.2G等
    :param limit_size: 限定大小，单位M
    :return:100M以下返回TRUE，否则返回FALSE
    """
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


def download_one_apk(url, save_path):
    """
    下载一个apk，下载完毕前，文件后缀为.tmp
    :param url: 下载链接
    :param save_path: apk保存路径
    :return:
    """
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
        os.rename(file_path, save_path)
        return True
    except Exception as e:
        print("线程名:{}, 下载出现问题!".format(threading.current_thread().name, e))
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(save_path):
            os.remove(save_path)
        return False


def acc_md5_hash(file_path, read_bytes=1024*8):
    md5obj = hashlib.md5()  # 创建一个md5算法对象
    with open(file_path, "rb") as f:  # 打开一个文件，必须是'rb'模式打开
        while True:
            data = f.read(read_bytes)  # 由于是一个文件，每次只读取固定字节
            if data:  # 当读取内容不为空时对读取内容进行update
                md5obj.update(f.read())
            else:  # 当整个文件读完之后停止update
                break
        ret = md5obj.hexdigest()  # 获取这个文件的MD5值
    # print(ret)
    return ret

