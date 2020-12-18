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

from dbentrust.redis_ import redisModule

if redisModule.name == "aioredis":
    # print("choose aioredis")
    from dbentrust.memobject.aiomemobject import *
elif redisModule.name == "txredisapi":
    # print("choose txredisapi")
    from dbentrust.memobject.txmemobject import *
elif redisModule.name == "redis":
    # print("choose redis")
    from dbentrust.memobject.memobject import *