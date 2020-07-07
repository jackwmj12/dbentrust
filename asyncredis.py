
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
    异步redis操作库的封装

    update on 2020-07-05
'''

from dbentrust import ASYNC

if ASYNC:
    import txredisapi as redis
    from twisted.internet import defer
else:
    import redis
    from redis import Redis
    from dbentrust.utils import defer


class asyncRedis(object):
    redis_conn = None
    
    def __init__(self,redis_conn=None):
        self.redis_conn = redis_conn
        
    if ASYNC:
        def init_app(self,config):
            self.redis_conn = redis.lazyConnectionPool(
                host=config.get("REDIS_HOST", "127.0.0.1"), password=config.get("REDIS_PASSWORD", None),
                port=config.get("REDIS_PORT", 6379),charset=config.get("REDIS_DECODE_RESPONSES", "utf-8"),
                connectTimeout=config.get("REDIS_CONNECT_TIMEOUT",10),
                dbid=config.get("REDIS_DB_ID",None),poolsize=config.get("REDIS_POOL_SIZE",3))
    else:
        def init_app(self, app):
            try:
                self.redis_conn = Redis(
                    connection_pool=redis.ConnectionPool(host=app.config.get('REDIS_HOST', '127.0.0.1'),
                                                         port=app.config.get('REDIS_PORT', 6379), decode_responses=True,
                                                         password=app.config.get('REDIS_PASSWORD', "Xyq107995")))
            except Exception as e:
                print(e)

    def getConn(self):
        return self.redis_conn
    
    @defer.inlineCallbacks
    def scan(self,start=0,pattern="*",count=10):
        '''

        :param pattern:
        :param start:
        :param count:
        :return:
        '''
        ret = yield self.redis_conn.scan(start,pattern,count)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def get(self, name):
        '''

        :param key:
        :return:
        '''
        ret = yield self.redis_conn.get(name)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def set(self,name,value,ex=0):
        '''

        :param key:
        :param value:
        :return:
        '''
        ret = yield self.redis_conn.set(name,value)
        if ex != 0:
            ret = yield self.redis_conn.expire(name, ex)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hget(self, name, *args):
        '''

        :param name:
        :param args:
        :return:
        '''
        ret = yield self.redis_conn.hget(name, *args)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hset(self, name, key,value):
        '''
        :param name:
		:param key:
		:param value:
		:return:
		'''
        ret = yield self.redis_conn.hset(name, key,value)
        defer.returnValue(ret)
    
    @defer.inlineCallbacks
    def hgetall(self, name):
        '''

        :param name:
        :param args:
        :return:
        '''
        ret = yield self.redis_conn.hgetall(name)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hmget(self, name, *args):
        '''

        :param name:
        :param args:
        :return:
        '''
        ret = yield self.redis_conn.hmget(name,*args)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hmget2dic(self, name, *args):
        '''

		:param name:
		:param args:
		:return:
		'''
        ret = yield self.redis_conn.hmget(name, *args)
        ret = dict(zip(*args,ret))
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hmset(self, name, kwargs, ex=0):
        '''
        :param key:
        :param dic:
        :param ex:
        :return:
        '''
        # print(kwargs)
        ret = yield self.redis_conn.hmset(name, kwargs)
        if ex != 0:
            ret = yield self.redis_conn.expire(name, ex)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def delete(self,*name):
        '''

        :param key:
        :return:
        '''
        ret = yield self.redis_conn.delete(*name)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hdel(self, name, *keys):
        '''

        :param key:
        :return:
        '''
        ret = yield self.redis_conn.hdel(name,*keys)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def getbit(self,name,offset):
        '''

        :param name:
        :param offset:
        :return:
        '''
        ret = yield self.redis_conn.getbit(name,offset)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def incr(self, name, amount=1):
        '''

        :param name:
        :param amount:
        :return:
        '''
        ret = yield self.redis_conn.incr(name, amount)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hincrby(self,name,key,amount=1):
        '''

        :param name:
        :param amount:
        :return:
        '''
        ret = yield self.redis_conn.hincrby(name,key,amount)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hincrbyfloat(self,name,key,amount=0.1):
        '''

        :param name:
        :param key:
        :param amount:
        :return:
        '''
        ret = yield self.redis_conn.hincrbyfloat(name,key,amount)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def lpush(self,name, *values):
        '''

        :param name:
        :param values:
        :return:
        '''
        ret = yield self.redis_conn.lpush(name,*values)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def lrange(self,name, start, end):
        '''

        :param name:
        :param start:
        :param end:
        :return:
        '''
        ret = yield self.redis_conn.lrange(name, start,end)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def exist(self, name):
        '''

        :param name:
        :param key:
        :return:
        '''
        ret = yield self.redis_conn.exists(name)
        defer.returnValue(ret)
    
    @defer.inlineCallbacks
    def keys(self,pattern):
        '''
        
        :param filter:
        :return:
        '''
        ret = yield self.redis_conn.keys(pattern)
        defer.returnValue(ret)
    
    @defer.inlineCallbacks
    def hexists(self, name, key):
        '''

        :param name:
        :param key:
        :return:
        '''
        ret = yield self.redis_conn.hexists(name, key)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def expire(self,name,ex=0):
        '''

        :param name:
        :param ex:
        :return:
        '''
        ret = yield self.redis_conn.expire(name,ex)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def ttl(self,name):
        '''

        :param name:
        :return:
        '''
        ret = yield self.redis_conn.ttl(name)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def dbsize(self):
        '''

        :return:
        '''
        ret = yield self.redis_conn.dbsize()
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def lindex(self,name,index):
        '''
        通过索引获取列表元素
        :param key:
        :return:
        '''
        ret = yield self.redis_conn.lindex(name,index)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def llen(self,key):
        '''
        获取列表长度
        :return:
        '''
        ret = yield self.redis_conn.llen(key)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def lpush(self,key,value):
        '''
        从左边推入一个数据
        :return:
        '''
        ret = yield self.redis_conn.lpush(key,value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def rpush(self, key, value):
        '''
		从右边推入一个数据
		:return:
		'''
        ret = yield self.redis_conn.rpush(key, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def lrange(self,key,start,end):
        ret = yield self.redis_conn.lrange(key,start,end)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def ltrim(self,key,start,end):
        ret = yield self.redis_conn.ltrim(key, start,end)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def lrem(self,key,start,value):
        ret = yield self.redis_conn.lrem(key, start, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def flushall(self):
        '''
        
        :return:
        '''
        ret = yield self.redis_conn.flushall()
        defer.returnValue(ret)