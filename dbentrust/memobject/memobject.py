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
    redis 关系对象
    通过key键的名称前缀来建立
    各个key-value 直接的关系
'''
from typing import Dict, Any, List
import redis
from redis import Redis

class MemConnectionManager:
    # _connection : Redis = None
    _connection = None

    @classmethod
    def setConnection(cls,connection):
        '''
        设置redis连接池
        :param connection asyncRedis
        '''
        # Log.debug("switch to {}".format(connection))
        cls._connection = connection

    @classmethod
    def getConnection(cls):
        '''
        获取redis连接池
        '''
        return cls._connection
    
    @classmethod
    def initConnection(cls,config):
        '''
        :return
        '''
        cls._connection = Redis(
                    connection_pool=redis.ConnectionPool(host=config.get('REDIS_HOST', '127.0.0.1'),
                                                         port=config.get('REDIS_PORT', 6379), decode_responses=True,
                                                         password=config.get('REDIS_PASSWORD', None)))
    
class MemCache:
    '''
     内存数据模型（value）
    '''
    _tablename_ = "Mem"
    _name_ = None

    def __init__(self, pk):
        '''
        :param pk:主键，一般为数据库内的 id,或者设备名称，编号等唯一值
        '''
        self._fk = 0
        self._admin = ""
        self._pk = str(pk)
        self.sync_count = 10

        self._key = None

    def __str__(self):
        return "<{}> : {} 数据为:\n {}".format(self._tablename_,self.key, dict(self))
    
    def __repr__(self):
        return "<{}> : {}".format(self._tablename_, self.key)
    
    def keys(self):
        '''
        返回一个tuple，该tuple决定了dict(self)所用到的键值
        :return
        '''
        return ()
        
    def setPK(self, pk):
        '''
        设置ID
        :param pk:
        :return:
        '''
        self._pk = pk

    def getPk(self):
        return self._pk

    def setFK(self, admin, fk):
        '''
        设置外键，若是关联数据，需要设置管理对象的id
        :param admin: 关联的admin对象的key
        :param fk :关联admin对象的pk
        :return:
        '''
        self._fk = str(fk)
        self._admin = "".join([str(admin) , ':'])
        self.produceKey()
        return self

    def produceKey(self):
        '''
        生成redis保存的key
        规则为：外键key + : + _tablename_ + : + 主键
        '''
        if self._pk:
            self._key = ''.join([self._admin, self._tablename_, ':', self._pk])
        else:
            self._key = ''.join([self._admin, self._tablename_])

    @property
    def key(self):
        '''
        保证每次需要使用 _key 时，同一个对象只会生成一次，减少cpu消耗
        :return:
        '''
        # Log.debug("使用_key")
        if not self._key:
            # Log.debug("载入/重载_key")
            # print("载入/重载_key")
            # print(self._pk)
            self.produceKey()
        return self._key

    def locked(self):
        '''
        检测对象是否被锁定
        '''
        # return MemConnectionManager.getConnection().get("_".join([self.key,"lock"]))

    def lock(self):
        '''
        锁定对象,暂定最长锁定时间为2S
        '''
        # return MemConnectionManager.getConnection().set("_".join([self.key,"lock"]), 1,2)

    def release(self):
        '''
        释放锁
        '''
        # return MemConnectionManager.getConnection().delete("_".join([self.key,"lock"]))

    def is_exist(self):
        return MemConnectionManager.getConnection().exists(self.key)

    def dbsize(self):
        '''

        :return:
        '''
        return MemConnectionManager.getConnection().dbsize()

    def delete(self):
        '''
        删除本对象映射的hash对象
        '''
        locked = self.locked()
        # Log.debug("检查字段是否被锁定")
        if not locked:
            # Log.debug("字段检查通过")
            self.lock()
            # Log.debug("拼接字段名称:{}".format(name))
            ret = MemConnectionManager.getConnection().delete(self.key)
            # Log.debug("设置字段值{}:{}".format(key,value))
            self.release()
            # Log.debug("解锁字段")
            return ret
        else:
            # Log.err("mdelete:该字段被锁定")
            return False

    def expire(self, ex=0):
        '''
        针对 本对象映射的哈希对象 进行超时赋值
        :param ex:
        :return:
        '''
        return MemConnectionManager.getConnection().expire(self.key, ex)

    def ttl(self):
        return MemConnectionManager.getConnection().ttl(self.key)
    
    def __getitem__(self, item):
        return getattr(self, item)

class MemValue(MemCache):
    '''
     内存数据模型（hash）
    '''
    _tablename_ = "MemValue"
    _name_ = "MemValue"

    def __init__(self, pk):
        '''
        :param pk:主键，一般为数据库内的 id,或者设备名称，编号等唯一值
        '''
        super(MemValue, self).__init__(pk)
        
        self.value = None

    def __str__(self):
        return "<{}> : {} 数据为:\n {}".format(self._tablename_,self.key,self.value)

    def get_value(self):
        '''
        针对单键值
        :return:
        '''
        return MemConnectionManager.getConnection().get(self.key)

    def update_value(self, value):
        '''
        修改本单个键值对象
        '''
        locked = self.locked()
        # Log.debug("检查字段是否被锁定")
        if not locked:
            # Log.debug("字段检查通过")
            self.lock()
            # Log.debug("拼接字段名称:{}".format(name))
            ret = MemConnectionManager.getConnection().set(self.key, value)
            # Log.debug("设置字段值{}:{}".format(key,value))
            self.release()
            # Log.debug("解锁字段")
            return ret
        else:
            # Log.err("update:该字段被锁定")
            return 1

    def get(self):
        '''
        针对单键值
        :return:
        '''
        ret = MemConnectionManager.getConnection().get(self.key)
        self.value = ret
        return self

    def update(self):
        '''
        修改本单个键值对象
        '''
        locked = self.locked()
        # Log.debug("检查字段是否被锁定")
        if not locked:
            # Log.debug("字段检查通过")
            self.lock()
            # Log.debug("拼接字段名称:{}".format(name))
            ret = MemConnectionManager.getConnection().set(self.key, self.value)
            # Log.debug("设置字段值{}:{}".format(key,value))
            self.release()
            # Log.debug("解锁字段")
            return ret
        else:
            # Log.err("update:该字段被锁定")
            return 1

class MemObject(MemCache):
    '''
     内存数据模型（hash）
    '''
    _tablename_ = "MemObject"

    _name_ = ""

    _zh_name_ = ""
    _type_ = ""
    _unit_ = ""
    
    def __init__(self, pk):
        '''
        :param pk:主键，一般为数据库内的 id,或者设备名称，编号等唯一值
        '''
        super(MemObject, self).__init__(pk)
    
    def __str__(self):
        return "<{}> : {} 数据为:\n {}".format(self._tablename_,self.key, dict(self))

    @classmethod
    @property
    def name(self):
        return self._name_

    @classmethod
    @property
    def zh_name(self):
        return self._zh_name_

    def get_local(self,key,default,type=str):
        return type(getattr(self,key,default))

    def get(self, key, default=None,type=str):
        '''
        本对象映射的哈希对象内的某个key值
        @:param key:需要获取的键值
        @:return str
        '''
        ret = MemConnectionManager.getConnection().hget(self.key, key)
        if ret is not None:
            return type(ret)
        else:
            return default

    def hmget2dic(self, name, *args):
        '''
		获取所有给定字段的值,并转换成dict
		:param name:
		:param args:
		:return:
		'''
        ret = MemConnectionManager.getConnection().hmget(name, *args)
        return dict(zip(*args, ret))

    def get_multi(self, *keys):
        '''
        一次获取本对象映射的哈希对象内的多个key的值
        @param keys: list(str) key的列表
        :return: dict
        '''
        values = MemConnectionManager.getConnection().hmget(self.key, keys)
        return self.get_from_list(keys, values)
    
    def get_multi2dic(self, *keys):
        '''
        一次获取本对象映射的哈希对象内的多个key的值
        @param keys: list(str) key的列表
        :return: dict
        '''
        values = MemConnectionManager.getConnection().hmget(self.key, keys)
        self.get_from_list(keys, values)
        return {key:self.__getitem__(key) for key in keys}
    
    def get_all(self):
        '''
        获取本对象映射的哈希对象内的所有值（keys里面定义的所有值，而非getall）
        :return: self
        '''
        keys = self.keys()
        values = MemConnectionManager.getConnection().hmget(self.key, keys)
        return self.get_from_list(keys, values)

    def get_all2dic(self) -> Dict:
        '''
        获取本对象映射的哈希对象内的所有值（keys里面定义的所有值，而非getall）
        :return: 字典
        '''
        keys = self.keys()
        values = MemConnectionManager.getConnection().hmget(self.key, keys)
        self.get_from_list(keys, values)
        return dict(self)
    
    def update(self, key, value):
        '''
        修改本对象映射的哈希对象里的单个键值
        '''
        locked = self.locked()
        # Log.debug("检查字段是否被锁定")
        if not locked:
            # Log.debug("字段检查通过")
            self.lock()
            # Log.debug("拼接字段名称:{}".format(name))
            ret = MemConnectionManager.getConnection().hset(self.key, key, value)
            # Log.debug("设置字段值{}:{}".format(key,value))
            self.release()
            # Log.debug("解锁字段")
            return ret
        else:
            # Log.err("update:该字段被锁定")
            return 1
    
    def update_multi(self, mapping):
        '''
        修改本对象映射的哈希对象里的多个键值
        '''
        locked = self.locked()
        # Log.debug("检查字段是否被锁定")
        if not locked:
            # Log.debug("字段检查通过")
            self.lock()
            # Log.debug("拼接字段名称:{}".format(name))
            ret = MemConnectionManager.getConnection().hmset(self.key, mapping)
            # Log.debug("设置字段值{}:{}".format(name,mapping))
            self.release()
            # Log.debug("解锁字段")
            return ret
        else:
            # Log.err("update_multi:该字段被锁定")
            return False
    
    def incr(self, key, delta):
        '''
        自增 本对象映射的哈希对象 的 _count 值，一般用于同步数据库
        '''
        locked = self.locked()
        # Log.debug("检查字段是否被锁定")
        if not locked:
            # Log.debug("字段检查通过")
            self.lock()
            # Log.debug("拼接字段名称:{}".format(name))
            ret = MemConnectionManager.getConnection().hincrby(self.key, key, delta)
            # Log.debug("设置字段值{}:{}".format(key,value))
            self.release()
            # Log.debug("解锁字段")
            return ret
        else:
            # Log.err("incr:该字段被锁定")
            return None
    
    def insert_without_sync(self):
        '''插入本对象映射的哈希对象
        '''
        # return self._insert().addCallback(self.syncDB).addErrback(DefferedErrorHandle)
        
        locked = self.locked()
        # Log.debug("检查字段是否被锁定")
        if not locked:
            # Log.debug("字段检查通过")
            self.lock()
            nowdict = dict(self)
            # Log.debug("拼接字段名称:{}".format(name))
            MemConnectionManager.getConnection().hmset(self.key, nowdict)
            # Log.debug("设置字段值{}:{}".format(key,value))
            
            self.release()
            
            return True
        else:
            return False

    def insert(self, curd=None):
        '''
        插入本对象映射的哈希对象，并进行 _count 计数，调用 syncDB
        '''
        # return self._insert().addCallback(self.syncDB).addErrback(DefferedErrorHandle)
    
        locked = self.locked()
        # Log.debug("检查字段是否被锁定")
        if not locked:
            # Log.debug("字段检查通过")
            self.lock()
        
            nowdict = dict(self)
            # Log.debug("拼接字段名称:{}".format(self.key))
            MemConnectionManager.getConnection().hmset(self.key, nowdict)
            # Log.debug("设置字段值{}".format(nowdict))
        
            count = MemConnectionManager.getConnection().hincrby(self.key, "_count", 1)
        
            self.release()
        
            self.syncDB(count, curd=curd)
        
            return True
        else:
            return False
    
    def syncDB(self, count,curd=None):
        '''
        本对象映射的哈希对象 内的数据同步到数据库
        :param count:
        :return:
        '''
        # Log.debug("%s count为：%s" % (self.__class__.__name__, count))
        if count:
            if count >= self.sync_count:
                # Log.debug("%s <%s>:已到同步时间：%s" % (self.__class__.__name__,self._pk, count))
                self.update("_count", 0)
                self.saveDB(curd=curd)
                return True
            else:
                # Log.debug("%s :还未到同步时间：%s" % (self.__class__.__name__, count))
                return False
        else:
            # Log.err("syncDB:该字段被锁定")
            return False
    
    def saveDB(self,curd=None):
        '''
        同步数据库操作，需要重写该函数
        :return:
        '''
        return None
    
    def get_from_dict(self, dic):
        '''
        将字典内的值依次赋予自身
        :param dic:
        :return: self
        '''
        for (k, v) in dic.items():
            if v != None:
                setattr(self, k, v)
        return self
    
    def get_from_list(self, keys, values):
        '''
        将列表内的值，赋予自身（顺序按照keys排列）
        :param list:
        :return:
        '''
        for i, key in enumerate(keys):
            if values[i] != None:
                setattr(self, key, values[i])
        return self

    def name2object(self, name):
        '''
        调用该函数可以通过redis中的key值
        转换成对应的mem对象
        子类需要重写才能实现该功能
        :param name:
        :return:
        '''
        name_ = name.split(self._tablename_ + ":")
        self._pk = name_[1]
        self._admin = name_[0]
        self._key = name
        return self
    
    def get_data(self):
        '''

        :return:
        '''
        return None

    @classmethod
    def scan(cls, start=0, count=1000) -> List:
        '''
        通过搜索手段返回内存内所有该对象
        :param start:
        :param count:
        :return: cls
        '''
        admins = []
        rets = []
        pattern = cls._tablename_ + ":*"
        while True:
            start, t_ = MemConnectionManager.getConnection().scan(start, pattern, count)
            if t_:
                admins += t_
            if not start:
                break
        ret = list(set(admins))
        for item in ret:
            split_item = item.split(":")
            if len(split_item) == 2:
                name_, id_ = split_item
                ret_ = cls(id_)
                rets.append(ret_)
        return rets

    @classmethod
    def scan2Name(cls, start=0, count=1000) -> list:
        '''
        通过搜索手段返回内存内所有该对象名称
        :param start:
        :param count:
        :return: cls
        '''
        admins = []
        pattern = cls._tablename_ + ":*"
        # pattern = cls._tablename_ +"[1,2,3,4,5,6,7,8,9,0]"
        while True:
            start, t_ = MemConnectionManager.getConnection().scan(start, pattern, count)
            if t_:
                admins += t_
            if not start:
                break
        ret = list(set(admins))
        return ret

class MemAdmin(MemObject):
    '''
        内存数据模型（hash），一般用于admin模型
    '''
    _tablename_ = "MemAdmin"

    def __init__(self, pk):
        '''
        root节点
        :param pk :Mode主键，以此区分不同对象
        '''
        super(MemAdmin, self).__init__(pk)

    def build_leaf(self,leaf,fk,dict):
        '''
        创建 子节点 对象，且插入数据
        :param object: 外键连接对象（MemObject 及其子类）
        :param fk:     MemObject 及其子类 的 主键
        :param dict:   字典数据
        :return: MemObject 及其子类
        '''
        ret = leaf(fk).setFK(self.key, self._pk)
        if dict:
            ret.get_from_dict(dict)
        return ret
    
    def build_empty_leaf(self,leaf,fk=""):
        '''
        创建 子节点 对象，不插入数据
        :param leaf:
        :param fk:
        :return:
        '''
        return leaf(fk).setFK(self.key, self._pk)
    
    def build_empty_relation(self, relation,fk=""):
        '''
        创建 relation 对象，但不读取内存数据
        :param relation : 对象
        :param fk : 子健标识
        :return:
        '''
        return relation(fk).setFK(self.key, self._pk)
    
    def insert_leaf(self, leaf, fk, dict):
        '''
        插入/更新 子节点对象，且更新内存数据
        :param leaf: 外键连接对象
        :param fk: 子健标识
        :param dict:   字典数据
        :return:
        '''
        return leaf(fk).setFK(self.key, self._pk).get_from_dict(dict).insert()
    
    def update_leaf(self, leaf, fk, dict):
        '''
        插入/更新 子节点对象，且更新内存数据
        :param leaf: 外键连接对象
        :param fk: 子健标识
        :param dict:   字典数据
        :return:
        '''
        return leaf(fk).setFK(self.key, self._pk).update_multi(dict)

    def is_leaf_exits(self,leaf,fk):
        '''
        :param leaf : 子健对象
        :param fk : 子健标识
        :return:
        '''
        return leaf(fk).setFK(self.key, self._pk).is_exist()

    def get_leaf(self,leaf,pk="",*keys):
        '''
        根据外键fk 获取单个外键相关对象
        :param object:  外键连接对象
        :return:
        '''
        if not keys:
            ret = leaf(pk).setFK(self.key,self._pk).get_all()
        else:
            ret = leaf(pk).setFK(self.key,self._pk).get_multi(*keys)
            # ret = leaf.get_from_dict(ret_)
        return ret

    def get_leaf2dic(self,leaf,pk="",*keys):
        '''
        从内存中获取单个子节点数据（dict）
        :param object:  外键连接对象
        :return:
        '''
        if not keys:
            return leaf(pk).setFK(self.key, self._pk).get_all2dic()
        else:
            return leaf(pk).setFK(self.key, self._pk).get_multi2dic(*keys)
        
    def get_leafs_by_relation(self,relation,pk="",start=0,pattern = "*",count=1000):
        '''
        通过 relation 表 取出所有外键相关key名称
        :param relation_name:
        :return:
        '''
        ret = []
        relation = relation(pk).setFK(self.key, self._pk)
        leafsnames = relation.get_leafs_by_relation(start,pattern,count)
        for leafsname in leafsnames:
            leaf = relation.name2object(leafsname)
            if leaf != None:
                ret.append(leaf)
        return ret

    def get_leafnames_by_relation(self, relation, pk="", start=0,pattern = "*", count=1000):
        '''
        通过 relation 表 取出所有外键相关key名称
        :param relation_name:
        :return:
        '''
        relation = relation(pk).setFK(self.key, self._pk)
        return relation.get_leafs_by_relation(start,pattern, count)

    def add_leafs_on_relation(self,relation,*leafs,pk=""):
        '''
        往 relation 表下 添加外键元素
        :param relation:
        :param pk:
        :param leafs:
        :return:
        '''
        relation = relation(pk).setFK(self.key, self._pk)
        return relation.add_leafs_on_relation(*leafs)
        
    def scan_leafnames(self,leaf,start=0,count=1000):
        '''
        搜索所有和该对象相关的 leaf 对象，并返回key值
        :param start:
        :param pattern:
        :param count:
        :return:
        '''
        keys = []
        leaf = leaf("").setFK(self.key,self._pk)
        pattern = leaf.key+":"+"*"
        while True:
            start,t_ = MemConnectionManager.getConnection().scan(start,pattern,count)
            if t_:
                keys += t_
            if not start:
                break
        return list(set(keys))

    def scan_leafs(self, leaf, start=0, count=1000):
        '''
        搜索该所有 子对象内 的 leaf 对象，并返回对象（并未从内存中获取填充数据）
        :param start:
        :param pattern:
        :param count:
        :return:
        '''
        leafs = []
        keys = self.scan_leafnames(leaf, start, count)
        for key in keys:
            l_ = leaf().name2object(key)
            if l_:
                leafs.append(l_)
        return leafs

class MemSet(MemCache):
    '''
    :param
    '''
    _tablename_ = "MemSet"

    def __init__(self, pk=''):
        '''
        :param pk :Mode主键，以此区分不同对象
        '''
        super(MemSet, self).__init__(pk)

    def count(self):
        '''
        获取与左外建相关的所有
        :return:
        '''
        return MemConnectionManager.getConnection().scard(self.key)

    def append(self, *objects):
        ''':param
        '''
        if isinstance(objects, (list,tuple)):
            if objects and isinstance(objects[0], MemCache):
                values = [item.key for item in objects]
            else:
                values = objects
        elif isinstance(objects,MemCache):
            values = objects.key
        else:
            values = objects

        if values:

            locked = self.locked()
            # Log.debug("检查字段是否被锁定")
            if not locked:
                # Log.debug("字段检查通过")
                self.lock()

                MemConnectionManager.getConnection().sadd(self.key, *values)

                self.release()

                return True
            
        return False

    def get_all(self,start=0, pattern=None, count=500):
        '''

        :param
        '''

        s = []
        while True:
            start, t_ = MemConnectionManager.getConnection().sscan(self.key,start, pattern, count)
            if t_:
                s += t_
            if not start:
                break
        return list(s)

    def remove(self,*objects):
        '''
        :param
        '''
        if isinstance(objects, (list,tuple)):
            if objects and isinstance(objects[0], MemCache):
                values = [item.key for item in objects]
            else:
                values = objects
        elif isinstance(objects,MemCache):
            values = objects.key
        else:
            values = objects

        locked = self.locked()
        # Log.debug("检查字段是否被锁定")
        if not locked:
            # Log.debug("字段检查通过")
            self.lock()

            MemConnectionManager.getConnection().srem(self.key,*values)

            self.release()

            return True
        
        return False

class MemList(MemCache):
    ''':param'''
    _tablename_ = "MemList"

    def __init__(self, pk=''):
        '''
        :param pk :Mode主键，以此区分不同对象
        '''
        super(MemList, self).__init__(pk)

    def count(self):
        '''
        获取与左外建相关的所有
        :return:
        '''
        return MemConnectionManager.getConnection().llen(self.key)

    def append(self, *objects):
        '''
        往关系表内添加数据
        :param value:
        :return:
        '''
        if isinstance(objects, (list,tuple)):
            if objects and isinstance(objects[0], MemCache):
                values = [item.key for item in objects]
            else:
                values = objects
        elif isinstance(objects,MemCache):
            values = objects.key
        else:
            values = objects

        locked = self.locked()
        # Log.debug("检查字段是否被锁定")
        if not locked:
            # Log.debug("字段检查通过")
            self.lock()

            MemConnectionManager.getConnection().lpush(self.key, *values)

            self.release()

            return True
        
        return False

    def remove(self, leaf, count=0):
        '''
        移除列表中下标从start开始的
        第一个值为value的数据
        :param count:
            count > 0 : 从表头开始向表尾搜索，移除与 VALUE 相等的元素，数量为 COUNT 。
            count < 0 : 从表尾开始向表头搜索，移除与 VALUE 相等的元素，数量为 COUNT 的绝对值。
            count = 0 : 移除表中所有与 VALUE 相等的值。
        :param value:
        :return:
        '''
        if isinstance(leaf, str):
            value = leaf
        else:
            value = leaf.key

        locked = self.locked()
        # Log.debug("检查字段是否被锁定")
        if not locked:
            # Log.debug("字段检查通过")
            self.lock()

            MemConnectionManager.getConnection().lrem(self.key, count, value)

            self.release()

            return True
        
        return False

    def get_by_index(self, index):
        return MemConnectionManager.getConnection().lindex(self.key, index)

    def get_all(self, start=0, end=1000):
        '''

        :param start:
        :param end:
        :return:
        '''
        # print(self.key)
        return MemConnectionManager.getConnection().lrange(self.key, start, end)

class MemSortedSet(MemCache):
    '''
    :param
    '''
    _tablename_ = "MemSortedSet"

    def __init__(self,pk=""):
        super(MemSortedSet, self).__init__(pk)

    def addMemByEntrust(self,mem,value):
        if isinstance(mem,MemCache):
            src = {
                mem.key:value
            }
        elif isinstance(mem,str):
            src={
                mem:value
            }
        else:
            raise Exception("mem type error")
        return MemConnectionManager.getConnection().zadd(self.key,src)

    def addMem(self,*mems):
        return MemConnectionManager.getConnection().zadd(self.key,*mems)

    def getCount(self):
        return MemConnectionManager.getConnection().zcard(self.key)

    def getMemCountInScoreRange(self,min, max):
        return MemConnectionManager.getConnection().zcount(self.key,min,max)

    def addScoreToMem(self,mem,amount):
        if isinstance(mem,MemCache):
            mem = mem.key
        elif isinstance(mem,str):
            pass
        else :
            raise Exception("mem type error")
        return MemConnectionManager.getConnection().zincrby(self.key,mem,amount)

    def getMemsByIndex(self,start, end, desc=False, withscores=True,
               score_cast_func=float):
        return MemConnectionManager.getConnection().zrange(
            self.key,start, end,desc=desc, withscores=withscores,
            score_cast_func=score_cast_func
        )

    def getMemsByScoreRange(self,min, max, start=0, num=100,
                      withscores=False, score_cast_func=float):
        return MemConnectionManager.getConnection().zrangebyscore(
            self.key,min, max, start=start, num=num,
            withscores=withscores, score_cast_func=score_cast_func
        )

    def getIndexOfMem(self,mem):
        if isinstance(mem,MemCache):
            mem = mem.key
        elif isinstance(mem,str):
            pass
        else :
            raise Exception("mem type error")
        return MemConnectionManager.getConnection().zrank(
            self.key,mem
        )

    def getMemsByMemRange(self,min, max, start=None, num=None):
        '''
        :param
        '''
        return MemConnectionManager.getConnection().zrangebylex(self.key, min, max, start=None, num=None)

    def getMemsByIndexSortedByScore(self,start, end, withscores=False,
                  score_cast_func=float):
        '''
        :param
        '''
        return MemConnectionManager.getConnection().zrevrange(self.key, start, end, withscores,
                  score_cast_func)

    def getMemsByScoreSortedByScore(self,max, min,start=0, num=100, withscores=False,score_cast_func=float):
        '''
        :param
        '''
        return MemConnectionManager.getConnection().zrevrangebyscore(self.key, max, min,start, num, withscores,
                  score_cast_func)

    def removeMems(self,*mems):
        return MemConnectionManager.getConnection().zrem(
            self.key,*mems
        )

    def removeMemsByIndex(self,min, max):
        ''':param'''
        return MemConnectionManager.getConnection().zremrangebyrank(self.key, min, max)

    def removeMemsByScoreRange(self,min, max):
        ''':param'''
        return MemConnectionManager.getConnection().zremrangebyscore(self.key, min, max)

    def getRankOfMem(self,mem):
        ''':param'''
        if isinstance(mem,MemCache):
            mem = mem.key
        elif isinstance(mem,str):
            pass
        else :
            raise Exception("mem type error")
        return MemConnectionManager.getConnection().zrevrank(self.key,mem)

    def getScoreOfMem(self,mem):
        if isinstance(mem,MemCache):
            mem = mem.key
        elif isinstance(mem,str):
            pass
        else :
            raise Exception("mem type error")
        return MemConnectionManager.getConnection().zscore(self.key,mem)

    def get_all(self, match="*", count=100, score_cast_func=float):
        '''
        :param
        '''
        i_ = 0
        mems = []
        while True:
            i_, mem_ = MemConnectionManager.getConnection().zscan(
                self.key, cursor=i_, match=match, count=count,
                score_cast_func=score_cast_func
            )
            mems += mem_
            if i_ == 0:
                break

        return mems

class MemRelation(MemSet):
    '''
    内存模型间的中间关系表
    1 * ADMIN 《-》 N * OBJECT
    '''
    _tablename_ = "MemRelation"
    _leafs_ = []
    _root_ = None

    def __init__(self, pk=''):
        '''
        :param pk :Mode主键，以此区分不同对象
        '''
        super(MemRelation, self).__init__(pk)

    def produceKey(self):
        '''
        生成redis保存的key
        规则为：外键key + : + _tablename_ + : + 主键
        '''
        self._key = ''.join([self._admin, self._tablename_])

    def add_leafs_on_relation(self, *leafs):
        '''
        同 append 方法，往 relation 表内插入 对象列表
        :param leafs:
        :return:
        '''
        return self.append(*leafs)

    def get_leafs_by_relation(self, start=0, pattern="*", count=500):
        '''

        :param start:
        :param end:
        :return:
        '''
        return self.get_all(start, pattern, count)

    def names2leafs(self, leafnames):
        '''

        :return:
        '''
        leafs = []
        for leafname in leafnames:
            leaf_ = self.name2object(leafname)
            if leaf_:
                leafs += leaf_.get_all2dic()
        return leafs

    def name2object(self, name):
        '''
        :return
        '''
        t = name.split(":")
        if len(t) == 5:
            # 'admin':'pk':'realation':'leaf':'index'
            admin, pk, relation, type, index = t
            for leaf in self._leafs_:
                if type == leaf._name_:
                    return leaf(index).setFK(admin + ":" + pk, pk)
        elif len(t) == 3:
            # 'realation':'leaf':'index'
            _, type, index = t
            for leaf in self._leafs_:
                if type == leaf._name_:
                    return leaf(index)
        return None

    @classmethod
    def register_leafs(cls,*leafs:MemCache):
        '''
        :return
        '''
        if leafs:
            cls._leafs_ += leafs

    @classmethod
    def register_root(cls,root:MemAdmin):
        '''
        :return
        '''
        if root:
            cls._root_ = root

