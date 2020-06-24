import pymysql
from utils.mylog import MyLogging
# MYSQL封装的操作类，提供基本的数据库操作函数
# 相关教程链接
# https://www.runoob.com/python3/python3-mysql.html


class MySQLUtils(object):
    def __init__(self, host="localhost", user_name=None, user_pwd=None, db_name=None, db_port=3306,
                 log_obj: MyLogging = None):

        self.__host = host
        self.__user_name = user_name
        self.__user_pwd = user_pwd
        self.__db_name = db_name
        self.__db_port = int(db_port)
        self.log_obj = log_obj
        self.db_conn = None
        self.cursor = None
        # self.__connct_db()
        self.__get_cursor()

    def __connct_db(self):
        self.db_conn = pymysql.connect(host=self.__host, user=self.__user_name,
                                       password=self.__user_pwd, database=self.__db_name,
                                       port=self.__db_port)
        return self.db_conn

    def __get_cursor(self):
        if self.db_conn is None:
            self.__connct_db()
        if self.cursor is None:
            self.cursor = self.db_conn.cursor()
        return self.cursor

    def insert(self, sql):
        try:
            # 执行sql语句
            self.db_conn.ping(reconnect=True)
            self.cursor = self.db_conn.cursor()
            index = self.cursor.execute(sql)
            # 提交到数据库执行
            self.db_conn.commit()
        except Exception as e:
            # 如果发生错误则回滚
            self.db_conn.rollback()
            raise RuntimeWarning("数据库插入失败,数据发生回滚操作,sql:{},异常信息{}".format(sql, e))
        return index

    # 查找所有数据
    def select_all(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    # 根据sql更新数据
    def updata(self, sql):
        try:
            index = self.cursor.execute(sql)
            # 提交到数据库执行
            self.db_conn.commit()
        except Exception as e:
            # 如果发生错误则回滚
            self.db_conn.rollback()
            raise RuntimeWarning("数据库updata更新失败，数据发生回滚操作,sql:{},异常信息{}".format(sql, e))
        return index

    def execute(self, sql):
        """
        通用执行，可用于删除数据
        :param sql:
        :return:
        """
        try:
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db_conn.commit()
        except Exception as e:
            # 如果发生错误则回滚
            self.db_conn.rollback()
            raise RuntimeWarning("execut函数，数据发生回滚操作,sql:{},异常信息{}".format(sql, e))
        return True

    def execute_all(self, sqls):
        """
        用来对多条sql语句进行同时操作，添加事物
        :param sqls:sql列表，存储多条需要共同执行的sql语句
        :return:
        """
        for sql in sqls:
            try:
                # 执行sql语句
                self.cursor.execute(sql)
            except Exception as e:
                # 如果发生错误则回滚
                self.db_conn.rollback()
                raise RuntimeWarning("execute_all函数，数据发生回滚操作,sql:{},异常信息{}".format(sql, e))
        # 提交到数据库执行
        self.db_conn.commit()
        return True

    def batch_insert(self, sqls):
        """
        用来对多条sql语句进行同时操作，添加事物
        :param sqls:sql列表，存储多条需要共同执行的sql语句,如果出现唯一属性重复异常，跳过继续执行
        :return:
        """
        for sql in sqls:
            try:
                # 执行sql语句
                self.cursor.execute(sql)
            except Exception as e:
                # 如果发生错误则回滚
                if e.args[0] == 1062:
                    if self.log_obj is not None:
                        path = sql.split(",")[-1].split(")")[0]
                        self.log_obj.info(path)
                    continue
                else:
                    self.db_conn.rollback()
                    raise RuntimeWarning("execute_all函数，数据发生回滚操作,sql:{},异常信息{}".format(sql, e))
        # 提交到数据库执行
        self.db_conn.commit()
        return True

    def close_db(self):
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
        if self.db_conn is not None:
            # 关闭数据库连接
            self.db_conn.close()
            self.db_conn = None


