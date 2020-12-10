'''
Created on 2019-11-22
@author: LCC
            ┏┓　　　┏┓
          ┏┛┻━━━┛┻┓
          ┃　　　━　　　┃
          ┃　┳┛　┗┳　┃
          ┃　　　　　　　┃
          ┃　　　┻　　　┃
          ┗━┓　　　┏━┛
              ┃　　　┃
              ┃　　　┗━━━┓
              ┃　　　　　　　┣┓
              ┃　　　　　　　┏┛
              ┗┓┓┏━┳┓┏┛
                ┃┫┫　┃┫┫
                ┗┻┛　┗┻┛
                 神兽保佑，代码无BUG!
@desc：
    异步mysql操作库的封装
'''
import itertools
from typing import Any

from twisted.enterprise import adbapi
from twisted.python import log

import pymysql
pymysql.install_as_MySQLdb()

class ReconnectingMixin:
    """MySQL 重新连接时， ConnectionPool 可以正确执行指定的操作，流程是：
    - 执行操作
    - 如果是连接错误，重新执行一次操作
    参考:
    - http://www.gelens.org/2008/09/12/reinitializing-twisted-connectionpool/
    - http://www.gelens.org/2009/09/13/twisted-connectionpool-revisited/
    - http://twistedmatrix.com/pipermail/twisted-python/2009-July/020007.html
    """

    def _myRunInteraction(self, interaction, *args, **kw):
        '''拷贝自 adbapi.ConnectionPool._runInteraction
        简化了 _runInteraction:

        - 去掉对俘获到的异常的打印，而是交给下面的 _runInteraction 处理
        - 取消 rollback 操作，有需要 rollback 的请注意，只是我从来没用过
        '''
        conn = self.connectionFactory(self)
        trans = self.transactionFactory(self, conn)
        result = interaction(trans, *args, **kw)
        trans.close()
        conn.commit()
        return result

    def _runInteraction(self, interaction, *args, **kw):
        try:
            return self._myRunInteraction(interaction, *args, **kw)
        except pymysql.OperationalError as e:
            if e.args[0] not in (2006, 2013):
                raise
            log.msg("MySQLdb: got error %s, retrying operation" % (e))
            conn = self.connections.get(self.threadID())
            self.disconnect(conn)
            # try the interaction again
            return self._myRunInteraction(interaction, *args, **kw)

class InsertIdMixin:
    """在Twisted下用MySQL adbapi获取自增id
    http://blog.sina.com.cn/s/blog_6262a50e0101nbqc.html
    """

    def runMySQLInsert(self, *args, **kw):
        return self.runInteraction(self._runMySQLInsert, *args, **kw)

    def _runMySQLInsert(self, trans, *args, **kw):
        trans.execute(*args, **kw)
        return trans.connection.insert_id()

class MultiQueryMixin:
    """返回多个结果集
    """

    def runMultiQuery(self, *args, **kw):
        return self.runInteraction(self._runMultiQuery, *args, **kw)

    def _runMultiQuery(self, trans, *args, **kw):
        result_sets = kw.pop("result_sets", None)

        trans.execute(*args, **kw)

        results = []
        for i in itertools.count():
            if not result_sets or i in result_sets:
                results.append(trans.fetchall())
            if not trans.nextset():
                break

        return results

class MySQLReConnectionPool(adbapi.ConnectionPool):
       """
       This connection pool will reconnect if the server goes away.  This idea was taken from:
       http://www.gelens.org/2009/09/13/twisted-connectionpool-revisited/
       """
       def _runInteraction(self, interaction, *args, **kw):
           try:
               return adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)
           except pymysql.OperationalError as e:
               if e.args[0] not in (2006, 2013):
                   raise
               log.err("Lost connection to MySQL, retrying operation.  If no errors follow, retry was successful.")
               conn = self.connections.get(self.threadID())
               self.disconnect(conn)
               return adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)

class txMysqlPipeline(object):

    def __init__(self, pool=None):
        self.connection_pool = pool

    @classmethod
    def from_settings(cls,config):
        '''
        初始化数据库异步连接池
        :param config: 配置对象
        :return: 返回数据库异步连接池
        '''
        connkw = {
            'host': config.get('DB_HOST','127.0.0.1'),
            'user': config.get('DB_USER','root'),
            'password': config.get('DB_PASSWORD'),
            'db': config.get('DB_NAME'),
            'port': config.get('DB_PORT',3306),
            'use_unicode': config.get('USE_UNICODE',True),
            'charset': config.get('DB_CHARSET','utf8mb4'),
            'cursorclass': pymysql.cursors.DictCursor,
            'cp_reconnect': True,
        }
        pool = MySQLReConnectionPool('MySQLdb', **connkw)
        return cls(pool)

    def init_app(self,config:Any):
        '''
        初始化数据库异步连接池
        :param config: 配置对象
        :return: 返回数据库异步连接池
        '''
        connkw = {
            'host': config.get('DB_HOST', '127.0.0.1'),
            'user': config.get('DB_USER', 'root'),
            'password': config.get('DB_PASSWORD'),
            'db': config.get('DB_NAME'),
            'port': config.get('DB_PORT', 3306),
            'use_unicode': config.get('USE_UNICODE', True),
            'charset': config.get('DB_CHARSET', 'utf8mb4'),
            'cursorclass': pymysql.cursors.DictCursor,
            'cp_reconnect':True,
        }
        self.connection_pool = MySQLReConnectionPool('MySQLdb', **connkw)

    def runQuery(self,sql, args=()):
        '''
        数据库的查询
        :param sql: sql 语句
        :param args: sql内部参数
        :return:
        '''
        return self.connection_pool.runQuery(sql, args)

    def runOperation(self,sql,args=()):
        '''
        数据库的增删改
        :param sql: sql语句
        :param args: sql内部参数
        :return:
        '''
        return self.connection_pool.runOperation(sql,args)

    def runInteration(self,sql,args=()):
        '''
        执行指定的数据操作
        :param sql: sql语句
        :param args: sql内部参数
        :return:
        '''
        return self.connection_pool.runInteration(self.operate_db,sql,args)

    def operate_db(self,cursor,sql,args):
        return cursor.execute(
            sql,args
        )

    def close(self):
        '''
        关闭连接池
        :return:
        '''
        self.connection_pool.close()