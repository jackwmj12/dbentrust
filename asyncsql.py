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

import pymysql
from twisted.enterprise import adbapi

class sqlPipeline(object):

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
		}
		pool = adbapi.ConnectionPool('pymysql', **connkw)
		return cls(pool)

	def init_app(self,config):
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
		}
		self.connection_pool = adbapi.ConnectionPool('pymysql', **connkw)

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