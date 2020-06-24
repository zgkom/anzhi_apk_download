# -*- coding: utf-8 -*-
import os
import logging
from configparser import ConfigParser, NoOptionError

"""
（1）getint(section, option)
获取section中option的值，返回int类型数据，所以该函数只能读取int类型的值。
（2）getboolean(section, option)
获取section中option的值，返回布尔类型数据，所以该函数只能读取boolean类型的值。
（3）getfloat(section, option)
获取section中option的值，返回浮点类型数据，所以该函数只能读取浮点类型的值。
（4）has_option(section, option)
检测指定section下是否存在指定的option，如果存在返回True，否则返回False。
（5）has_section(section)
检测配置文件中是否存在指定的section，如果存在返回True，否则返回False。
"""


class Config(object):
    """定义一个读取配置文件的类"""
    __instance = None

    def __init__(self, config_file_path=None):
        #加载指定配置文件
        self.config_file_path = config_file_path or os.path.join(os.path.dirname(__file__), 'config.ini')
        logging.debug('配置初始化')
        self.config = ConfigParser()
        self.load_config()

    def load_config(self):
        logging.debug('加载配置')
        self.config.read(self.config_file_path, 'utf-8')

    @staticmethod
    def get_instance():
        if Config.__instance:
            return Config.__instance
        else:
            Config.__instance = Config()
        return Config.__instance

    def get_dict_by_section(self, section):
        opts = {}
        options = self.config.options(section)
        for key in options:
            value = self.config.get(section, key)
            opts[key] = value
        return opts

    def get_by_section_and_option(self,section,option):
        #通过字段和选项获得配置内容
        if self.config.has_section(section) and self.config.has_option(section, option):
            try:
                return self.config.get(section, option)
            except NoOptionError:
                return None
        else:
            return None

    def get(self, key):
        """
        获取配置
        :param str key: 格式 [section].[key] 如：app.name
        :return:如果没有按照格式或者配置中不存在相关配置，返回None
        """
        map_key = key.split('.')
        if len(map_key) < 2:
            return None
        section = map_key[0]
        # sections = self.config.sections()
        if not self.config.has_section(section):
            return None
        option = '.'.join(map_key[1:])
        try:
            return self.config.get(section, option)
        except NoOptionError:
            return None


def get(key, default=None):
    """
    获取配置
    :param str key: 格式 [section].[key] 如：app.name
    :return:
    """
    return Config.get_instance().get(key)


if __name__ == "__main__":
    #如果不事先创建对象，默认加载本路径中的myconfig.ini文件
    content = get("lua_script.CAPTURE_NAME")
    print(content)

    #加载指定配置文件
    config_path = r"E:\prototype\Test3\myconfig\myconfig.ini"
    myconfig = Config(config_path)
    #获得labels_and_model字段下的DETECTION_MODEL配置项
    model_path = myconfig.get("labels_and_model.DETECTION_MODEL")
    print(model_path)

    #获得配置文件中全部字段
    print(myconfig.config.sections())
    #获得某一字段下的所有选项
    print(myconfig.config.options("labels_and_model"))
    print(myconfig.get_by_section_and_option(section="labels_and_model",option="DETECTION_MODEL"))

