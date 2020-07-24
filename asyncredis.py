
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
    def getrange(self, name, start, end):
        '''
        返回 key 中字符串值的子字符
        :param
        '''
        ret = yield self.redis_conn.getrange(name, start, end)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def getset(self, name, value):
        '''
        将给定 key 的值设为 value ，并返回 key 的旧值(old value)。
        :param
        '''
        ret = yield self.redis_conn.getset(name, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def mget(self, name, *args):
        '''
        获取所有(一个或多个)给定 key 的值
        :param
        '''
        ret = yield self.redis_conn.getrange(name, *args)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def setbit(self, name, offset, value):
        '''
        对 key 所储存的字符串值，设置或清除指定偏移量上的位(bit)。
        :param
        '''
        ret = yield self.redis_conn.setbit(name, offset, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def setex(self, name, time, value):
        '''
        将值 value 关联到 key ，并将 key 的过期时间设为 seconds (以秒为单位)。
        :param
        '''
        ret = yield self.redis_conn.setex(name, time, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def setnx(self, name, value):
        '''
        只有在 key 不存在时设置 key 的值。
        :param
        '''
        ret = yield self.redis_conn.setnx(name, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def setrange(self, name, offset, value):
        '''
        用 value 参数覆写给定 key 所储存的字符串值，从偏移量 offset 开始。
        :param
        '''
        ret = yield self.redis_conn.setrange(name, offset, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def strlen(self, name):
        '''
        :param
        '''
        ret = yield self.redis_conn.strlen(name)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def mset(self, *args, **kwargs):
        '''
        同时设置一个或多个 key-value 对。
        :param
        '''
        ret = yield self.redis_conn.mset(*args, **kwargs)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def msetnx(self, *args, **kwargs):
        '''
        同时设置一个或多个 key-value 对，当且仅当所有给定 key 都不存在。
        :param
        '''
        ret = yield self.redis_conn.msetnx(*args, **kwargs)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def psetex(self, name, time_ms, value):
        '''
        这个命令和 SETEX 命令相似，
        但它以毫秒为单位设置 key 的生存时间，
        而不是像 SETEX 命令那样，以秒为单位。
        :param
        '''
        ret = yield self.redis_conn.psetex(name, time_ms, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hget(self, name, *args):
        '''
        获取存储在哈希表中指定字段的值。
        :param name:
        :param args:
        :return:
        '''
        ret = yield self.redis_conn.hget(name, *args)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hset(self, name, key,value):
        '''
        将哈希表 key 中的字段 field 的值设为 value 。
        :param name:
        :param key:
        :param value:
        :return:
        '''
        ret = yield self.redis_conn.hset(name, key,value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hsetnx(self, name, key, value):
        '''
        只有在字段 field 不存在时，设置哈希表字段的值。
        :param name:
        :param key:
        :param value:
        '''
        ret = yield self.redis_conn.hsetnx(name, key, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hvals(self, name):
        '''
        获取哈希表中所有值。
        :param
        '''
        ret = yield self.redis_conn.hvals(name)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hscan(self,name, cursor=0, match=None, count=None):
        '''
        迭代哈希表中的键值对。
        :param
        '''
        ret = yield self.redis_conn.hscan(name, cursor, match, count)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hgetall(self, name):
        '''
        获取在哈希表中指定 key 的所有字段和值
        :param name:
        :return:
        '''
        ret = yield self.redis_conn.hgetall(name)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hmget(self, name, *args):
        '''
        获取所有给定字段的值
        :param name:
        :param args:
        :return:
        '''
        ret = yield self.redis_conn.hmget(name,*args)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hmget2dic(self, name, *args):
        '''
        获取所有给定字段的值,并转换成dict
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
        同时将多个 field-value (域-值)对设置到哈希表 key 中。
        :param key:
        :param dic:
        :param ex:
        :return:
        '''
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
        删除一个或多个哈希表字段
        :param key:
        :return:
        '''
        ret = yield self.redis_conn.hdel(name,*keys)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def getbit(self,name,offset):
        '''
        对 key 所储存的字符串值，获取指定偏移量上的位(bit)。
        :param name:
        :param offset:
        :return:
        '''
        ret = yield self.redis_conn.getbit(name,offset)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def incr(self, name, amount=1):
        '''
        将 key 中储存的数字值增一。
        :param name:
        :param amount:
        :return:
        '''
        ret = yield self.redis_conn.incr(name, amount)
        defer.returnValue(ret)

    def incrby(self, name, amount=1):
        '''
        将 key 中储存的数字值增一。
        :param name:
        :param amount:
        :return:
        '''
        return self.incr(name, amount)

    @defer.inlineCallbacks
    def incrbyfloat(self, name, amount=1.0):
        '''
        将 key 所储存的值加上给定的浮点增量值（increment） 。
        :param
        '''
        ret = yield self.redis_conn.incrbyfloat(name, amount)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def decr(self, name, amount=1):
        '''
        将 key 中储存的数字值减一。
        :param
        '''
        ret = yield self.redis_conn.decr(name, amount)
        defer.returnValue(ret)

    def decrby(self, name, amount=1):
        '''
        key 所储存的值减去给定的减量值（decrement）
        :param
        '''
        return self.decr(name,amount)

    @defer.inlineCallbacks
    def append(self, name, *values):
        '''
        如果 key 已经存在并且是一个字符串，
        APPEND 命令将指定的 value 追加到该 key 原来值（value）的末尾。
        :param
        '''
        ret = yield self.redis_conn.append(name, *values)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hincrby(self,name,key,amount=1):
        '''
        为哈希表 name 中的指定字段key的整数值加上增量 increment 。
        :param name:
        :param key:
        :param amount:
        :return:
        '''
        ret = yield self.redis_conn.hincrby(name,key,amount)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hincrbyfloat(self,name,key,amount=0.1):
        '''
        为哈希表 name 中的指定 key 字段的浮点数值加上增量 increment 。
        :param name:
        :param key:
        :param amount:
        :return:
        '''
        ret = yield self.redis_conn.hincrbyfloat(name,key,amount)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hkeys(self, name):
        '''
        获取所有哈希表中的字段
        :param
        '''
        ret = yield self.redis_conn.hkeys(name)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def hlen(self, name):
        '''
        获取哈希表中字段的数量
        :param
        '''
        ret = yield self.redis_conn.hlen(name)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def blpop(self,name,timeout=0):
        '''
        移出并获取列表的第一个元素， 如果列表没有元素会阻塞列表直到等待超时或发现可弹出元素为止。
        :param
        '''
        ret = yield self.redis_conn.blpop(name,timeout)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def brpop(self, name,timeout=0):
        '''
        移出并获取列表的最后一个元素， 如果列表没有元素会阻塞列表直到等待超时或发现可弹出元素为止。
        :param
        '''
        ret = yield self.redis_conn.brpop(name,timeout)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def lpop(self, name):
        '''
        移出并获取列表的最后一个元素， 如果列表没有元素会阻塞列表直到等待超时或发现可弹出元素为止。
        :param
        '''
        ret = yield self.redis_conn.lpop(name)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def rpop(self, name):
        '''
        移除列表的最后一个元素，返回值为移除的元素。
        :param
        '''
        ret = yield self.redis_conn.rpop(name)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def rpoplpush(self, src, dst):
        '''
        移除列表的最后一个元素，并将该元素添加到另一个列表并返回
        :param
        '''
        ret = yield self.redis_conn.rpoplpush(src, dst)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def brpoplpush(self,src, dst, timeout=0):
        '''
        从列表中弹出一个值，将弹出的元素插入到另外一个列表中并返回它；
        如果列表没有元素会阻塞列表直到等待超时或发现可弹出元素为止。
        :param
        '''
        ret = yield self.redis_conn.brpoplpush(src, dst, timeout)
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
        查看哈希表 key 中，指定的字段是否存在。
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
    def linsert(self, name, where, refvalue, value):
        '''
        在列表的元素前或者后插入元素
        :param
        '''
        ret = yield self.redis_conn.linsert(name, where, refvalue, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def llen(self,name):
        '''
        获取列表长度
        :return:
        '''
        ret = yield self.redis_conn.llen(name)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def lpush(self,name,*value):
        '''
        从左边推入一个数据
        :return:
        '''
        ret = yield self.redis_conn.lpush(name,*value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def lpushx(self, name, value):
        '''
        将一个值插入到已存在的列表头部
        :param
        '''
        ret = yield self.redis_conn.lpushx(name, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def rpush(self, name, *value):
        '''
        在列表中添加一个或多个值
        :return:
        '''
        ret = yield self.redis_conn.rpush(name, *value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def rpushx(self, name, value):
        '''
        为已存在的列表添加值
        :param
        '''
        ret = yield self.redis_conn.rpushx(name, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def lrange(self,name,start,end):
        '''
        获取列表指定范围内的元素
        :param
        '''
        ret = yield self.redis_conn.lrange(name,start,end)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def ltrim(self,name,start,end):
        '''
        对一个列表进行修剪(trim)，就是说，
        让列表只保留指定区间内的元素，不在指定区间之内的元素都将被删除。
        :param
        '''
        ret = yield self.redis_conn.ltrim(name, start,end)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def lrem(self,key,start,value):
        '''
        移除列表元素
        :param
        '''
        ret = yield self.redis_conn.lrem(key, start, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def lset(self, name, index, value):
        '''
        通过索引设置列表元素的值
        :param
        '''
        ret = yield self.redis_conn.lset(name, index, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def scard(self,key):
        '''
        获取集合的成员数
        :param
        '''
        ret = yield self.redis_conn.scard(key)
        defer.returnValue(ret)
    
    @defer.inlineCallbacks
    def sadd(self,key,*values):
        '''
        向集合添加一个或多个成员
        :param
        '''
        try:
            ret = yield self.redis_conn.sadd(key,*values)
            defer.returnValue(ret)
        except Exception as e:
            print(e)

    @defer.inlineCallbacks
    def sdiff(self,key1,*keys):
        '''
        返回给定所有集合的差集
        :param
        '''
        ret = yield self.redis_conn.sdiff(key1,*keys)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def sdiffstore(self,destination, key1, *keys):
        '''
        返回给定所有集合的差集并存储在 destination 中
        :param
        '''
        ret = yield self.redis_conn.sdiffstore(destination,key1, *keys)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def sinter(self,key1,*keys):
        '''
        返回给定所有集合的交集
        :param
        '''
        ret = yield self.redis_conn.sinter(key1, *keys)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def sinterstore(self,destination,key1,*keys):
        '''
        返回给定所有集合的交集并存储在 destination 中
        :param
        '''
        ret = yield self.redis_conn.sinterstore(destination,key1, *keys)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def sismember(self,key1,member):
        '''
        判断 member 元素是否是集合 key 的成员
        :param
        '''
        ret = yield self.redis_conn.sismember(key1, member)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def smembers(self,key1):
        '''
        返回集合中的所有成员
        :param
        '''
        ret = yield self.redis_conn.smembers(key1)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def smove(self,source,destination,member):
        '''
        将 member 元素从 source 集合移动到 destination 集合
        :param
        '''
        ret = yield self.redis_conn.smove(source,destination,member)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def srandmember(self,key, count = None):
        '''
        返回集合中一个或多个随机数
        :param
        '''
        ret = yield self.redis_conn.srandmember(key, count)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def srem(self,key,*members):
        '''
        移除集合中一个或多个成员
        :param
        '''
        ret = yield self.redis_conn.srem(key,*members)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def sunion(self,key,*keys):
        '''
        返回所有给定集合的并集
        :param
        '''
        ret = yield self.redis_conn.sunion(key, *keys)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def sunionstore(self,destination,key,*keys):
        '''
        所有给定集合的并集存储在 destination 集合中
        :param
        '''
        ret = yield self.redis_conn.sunionstore(destination,key, *keys)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def sscan(self,key, cursor=0, match=None, count=None):
        '''
        迭代集合中的元素
        :param
        '''
        ret = yield self.redis_conn.sscan(key, cursor, match, count)
        defer.returnValue(ret)

    if ASYNC:
        @defer.inlineCallbacks
        def zadd(self, name, *args):
            '''
            向有序集合添加一个或多个成员，或者更新已存在成员的分数
            :param
            '''
            pieces = []
            for arg in args:
                for mem in arg.items():
                    pieces.append(mem[1])
                    pieces.append(mem[0])
            ret = yield self.redis_conn.zadd(name,*pieces)
            defer.returnValue(ret)
    else:
        @defer.inlineCallbacks
        def zadd(self, name, *args):
            '''
			向有序集合添加一个或多个成员，或者更新已存在成员的分数
			:param
			'''
            ret = yield self.redis_conn.zadd(name, score=None, member=None, *args)
            defer.returnValue(ret)

    @defer.inlineCallbacks
    def zcard(self, name):
        '''
        获取有序集合的成员数
        :param
        '''
        ret = yield self.redis_conn.zcard(name)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def zcount(self, name, min, max):
        '''
        计算在有序集合中指定区间分数的成员数
        :param
        '''
        ret = yield self.redis_conn.zcount(name, min, max)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def zincrby(self, name, value, amount=1.0):
        '''
        有序集合中对指定成员的分数加上增量 increment
        :param
        '''
        ret = yield self.redis_conn.zincrby(name, amount, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def zinterstore(self, dest, keys, aggregate=None):
        '''
        计算给定的一个或多个有序集的交集并将结果集存储在新的有序集合 key 中
        :param
        '''
        ret = yield self.redis_conn.zinterstore(dest, keys, aggregate=None)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def zlexcount(self, name, min, max):
        '''
        在有序集合中计算指定字典区间内成员数量
        :param
        '''
        ret = yield self.redis_conn.zlexcount(name, min, max)
        defer.returnValue(ret)

    if ASYNC:
        @defer.inlineCallbacks
        def zrange(self, name, start, end, desc=False, withscores=False,
                   score_cast_func=float):
            '''
            通过索引区间返回有序集合指定区间内的成员
            :param
            '''
            ret = yield self.redis_conn._zrange(name, start, end,withscores=withscores,reverse=desc)
            defer.returnValue(ret)
    else:
        @defer.inlineCallbacks
        def zrange(self, name, start, end, desc=False, withscores=False,
                   score_cast_func=float):
            '''
            通过索引区间返回有序集合指定区间内的成员
            :param
            '''
            ret = yield self.redis_conn.zrange(name, start, end,
                   desc=desc, withscores=withscores,score_cast_func=score_cast_func)
            defer.returnValue(ret)

    if ASYNC:
        @defer.inlineCallbacks
        def zrangebylex(self, name, min, max, start=None, num=None):
            '''
			通过字典区间返回有序集合的成员
			:param
			'''
            raise Exception("no method 'zrangebylex'")
    else:
        @defer.inlineCallbacks
        def zrangebylex(self, name, min, max, start=None, num=None):
            '''
			通过字典区间返回有序集合的成员
			:param
			'''
            ret = yield self.redis_conn.zrangebylex(name, min, max, start, num)
            defer.returnValue(ret)

    if ASYNC:
        @defer.inlineCallbacks
        def zrangebyscore(self, name, min, max, start=None, num=None,
                          withscores=False, score_cast_func=float):
            '''
            通过分数返回有序集合指定区间内的成员
            :param
            '''
            ret = yield self.redis_conn.zrangebyscore(name, min, max, offset=start, count=num,
                          withscores=withscores)
            defer.returnValue(ret)
    else:
        @defer.inlineCallbacks
        def zrangebyscore(self, name, min, max, start=None, num=None,
                          withscores=False, score_cast_func=float):
            '''
			通过分数返回有序集合指定区间内的成员
			:param
			'''
            ret = yield self.redis_conn.zrangebyscore(name, min, max, start, num,
                  withscores,score_cast_func=score_cast_func)
            defer.returnValue(ret)

    @defer.inlineCallbacks
    def zrank(self, name, value):
        '''
        返回有序集合中指定成员的索引
        :param
        '''
        ret = yield self.redis_conn.zrank(name, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def zrem(self, name, *values):
        '''
        移除有序集合中的一个或多个成员
        :param
        '''
        ret = yield self.redis_conn.zrem(name, *values)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def zremrangebylex(self, name, min, max):
        '''
        移除有序集合中给定的字典区间的所有成员
        :param
        '''
        ret = yield self.redis_conn.zremrangebylex(name, min, max)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def zremrangebyrank(self, name, min, max):
        '''
        移除有序集合中给定的排名区间的所有成员(从小到大)
        :param
        '''
        ret = yield self.redis_conn.zremrangebyrank(name, min, max)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def zremrangebyscore(self, name, min, max):
        '''
        移除有序集合中给定的分数区间的所有成员
        :param
        '''
        ret = yield self.redis_conn.zremrangebyscore(name, min, max)
        defer.returnValue(ret)

    if ASYNC:
        @defer.inlineCallbacks
        def zrevrange(self, name, start, end, withscores=False,
                      score_cast_func=float):
            '''
            返回有序集中指定区间内的成员，通过索引，分数从高到低
            :param
            '''
            ret = yield self.redis_conn.zrevrange(name, start, end, withscores)
            defer.returnValue(ret)
    else:
        @defer.inlineCallbacks
        def zrevrange(self, name, start, end, withscores=False,
                      score_cast_func=float):
            '''
			返回有序集中指定区间内的成员，通过索引，分数从高到低
			:param
			'''
            ret = yield self.redis_conn.zrevrange(name, start, end, withscores,
                                                  score_cast_func)
            defer.returnValue(ret)

    if ASYNC:
        @defer.inlineCallbacks
        def zrevrangebyscore(self, name, max, min, start=None, num=None,
                             withscores=False, score_cast_func=float):
            '''
            返回有序集中指定分数区间内的成员，分数从高到低排序
            :param
            '''
            ret = yield self.redis_conn.zrevrangebyscore(name, max, min,
                             withscores,offset=start, count=num)
            defer.returnValue(ret)
    else:
        @defer.inlineCallbacks
        def zrevrangebyscore(self, name, max, min, start=None, num=None,
                             withscores=False, score_cast_func=float):
            '''
			返回有序集中指定分数区间内的成员，分数从高到低排序
			:param
			'''
            ret = yield self.redis_conn.zrevrangebyscore(name, max, min, start, num,
                                                         withscores, score_cast_func)
            defer.returnValue(ret)

    @defer.inlineCallbacks
    def zrevrank(self, name, value):
        '''
        返回有序集合中指定成员的排名，有序集成员按分数值递减(从大到小)排序
        :param
        '''
        ret = yield self.redis_conn.zrevrank(name, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def zscore(self, name, value):
        '''
        返回有序集中，成员的分数值
        :param
        '''
        ret = yield self.redis_conn.zscore(name, value)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def zunionstore(self, dest, keys, aggregate=None):
        '''
        计算给定的一个或多个有序集的并集，并存储在新的 key 中
        :param
        '''
        ret = yield self.redis_conn.zunionstore(dest, keys, aggregate)
        defer.returnValue(ret)

    if ASYNC:
        @defer.inlineCallbacks
        def zscan(self, name, cursor=0, match=None, count=None,
                  score_cast_func=float):
            '''
            迭代有序集合中的元素（包括元素成员和元素分值）
            :param
            '''
            ret = yield self.redis_conn.zscan(name, cursor, match, count)
            defer.returnValue(ret)
    else:
        @defer.inlineCallbacks
        def zscan(self, name, cursor=0, match=None, count=None,
                  score_cast_func=float):
            '''
			迭代有序集合中的元素（包括元素成员和元素分值）
			:param
			'''
            ret = yield self.redis_conn.zscan(name, cursor, match, count,
                                              score_cast_func)
            defer.returnValue(ret)

    @defer.inlineCallbacks
    def flushall(self):
        '''

        :return:
        '''
        ret = yield self.redis_conn.flushall()
        defer.returnValue(ret)

    def createSession(self):
        '''
        :param
        '''
        # return self.redis_conn.pipeline()
        return self.redis_conn.multi()
