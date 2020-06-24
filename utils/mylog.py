import logging
from logging.handlers import RotatingFileHandler
import os
import sys


class MyLogging(object):
    def __init__(self, set_level="debug",
                 name=os.path.split(os.path.splitext(sys.argv[0])[0])[-1],
                 log_path=None,
                 log_formatter="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                 use_console=True,
                 maxBytes=10 * 1024 * 1024,
                 backupCount=1):
        """
        :param set_level: 设置日志的打印级别，默认为DEBUG
        :param name: 日志中将会打印的name，默认为运行程序的name
        :param log_path: 日志写入的文件，默认为None，不写入任何文件
        :param log_formatter:日志的输出格式
        :param use_console:是否在控制台打印，默认为True
        :param maxBytes:如果日志写入文件，文件最大写入字节数，默认8M
        :param backupCount:日志最大回滚数量，默认为1
        """
        self.logger = logging.getLogger(name)
        if set_level.lower() == "critical":
            self.logger.setLevel(logging.CRITICAL)
        elif set_level.lower() == "error":
            self.logger.setLevel(logging.ERROR)
        elif set_level.lower() == "warning":
            self.logger.setLevel(logging.WARNING)
        elif set_level.lower() == "info":
            self.logger.setLevel(logging.INFO)
        elif set_level.lower() == "debug":
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.NOTSET)

        log_root = os.path.dirname(log_path)
        if not os.path.exists(log_root):
            os.makedirs(log_root)
        self.log_formatter = log_formatter
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        # 添加输出源
        if log_path is not None:
            # 定义一个RotatingFileHandler，最多备份3个日志文件，每个日志文件最大8M
            self.log_rhandler = RotatingFileHandler(log_path, encoding='utf-8', maxBytes=self.maxBytes, backupCount=self.backupCount)
            self.log_rhandler.setFormatter(logging.Formatter(self.log_formatter))
            self.logger.addHandler(self.log_rhandler)
        else:
            self.log_rhandler = None
        if use_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(self.log_formatter))
            self.logger.addHandler(console_handler)

    def __addHandler(self, hdlr):
        #添加输入平台
        self.logger.addHandler(hdlr)

    def __removeHandler(self, hdlr):
        self.logger.removeHandler(hdlr)

    def critical(self, msg, log_path=None, *args, **kwargs):
        if log_path is not None:
            self.change_log_file(log_path)
        #最高级别
        self.logger.critical(msg, *args, **kwargs)

    def warning(self, msg, log_path=None, *args, **kwargs):
        if log_path is not None:
            self.change_log_file(log_path)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, log_path=None, *args, **kwargs):
        if log_path is not None:
            self.change_log_file(log_path)
        self.logger.error(msg, *args, **kwargs)

    def change_log_file(self, new_log_path):
        if self.log_rhandler is not None:
            self.__removeHandler(self.log_rhandler)
        # 添加输出源
        # 定义一个RotatingFileHandler，最多备份3个日志文件，每个日志文件最大8M
        self.log_rhandler = RotatingFileHandler(new_log_path, encoding='utf-8', maxBytes=self.maxBytes,
                                                backupCount=self.backupCount)
        self.log_rhandler.setFormatter(logging.Formatter(self.log_formatter))
        self.logger.addHandler(self.log_rhandler)

    def info(self, msg, log_path=None, *args, **kwargs):
        if log_path is not None:
            self.change_log_file(log_path)
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, log_path=None, *args, **kwargs):
        if log_path is not None:
            self.change_log_file(log_path)
        self.logger.debug(msg, *args, **kwargs)

    def log(self, level, msg, log_path=None, *args, **kwargs):
        if log_path is not None:
            self.change_log_file(log_path)
        #自定义日志级别
        self.logger.log(level, msg, *args, **kwargs)
