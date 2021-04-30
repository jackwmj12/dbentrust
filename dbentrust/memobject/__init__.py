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

from dbentrust.main import redisModule

if redisModule.name == "aioredis":
    from dbentrust.memobject.aiomemobject import MemConnectionManager, MemCache, MemValue, MemObject, MemAdmin, MemSet, MemList, MemSortedSet, MemRelation
elif redisModule.name == "txredisapi":
    from dbentrust.memobject.txmemobject import MemConnectionManager, MemCache, MemValue, MemObject, MemAdmin, MemSet, MemList, MemSortedSet, MemRelation
elif redisModule.name == "redis":
    from dbentrust.memobject.memobject import MemConnectionManager, MemCache, MemValue, MemObject, MemAdmin, MemSet, MemList, MemSortedSet, MemRelation

__all__ = ["MemConnectionManager", "MemCache", "MemValue","MemObject","MemAdmin","MemSet","MemList","MemSortedSet","MemRelation"]