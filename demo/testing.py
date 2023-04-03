# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : testing.py
# @Time     : 2023-03-22 18:08
# @Software : dbentrust
# @Email    : jackwmj12@163.com
# @Github   : 
# @Desc     : 
#            ┏┓      ┏┓
#          ┏┛┻━━━┛┻┓
#          ┃      ━      ┃
#          ┃  ┳┛  ┗┳  ┃
#          ┃              ┃
#          ┃      ┻      ┃
#          ┗━┓      ┏━┛
#              ┃      ┃
#              ┃      ┗━━━┓
#              ┃              ┣┓
#              ┃              ┏┛
#              ┗┓┓┏━┳┓┏┛
#                ┃┫┫  ┃┫┫
#                ┗┻┛  ┗┻┛
#                 神兽保佑，代码无BUG!
#
#
#

from dbentrust.aiomemobject import MemAdmin, MemObject

class A(MemAdmin):
    _tablename_ = "a"

class A1(MemObject):
    _tablename_ = "a1"

a = A("1").build_empty_leaf(A1,"2")
a1 = A1("2").setAdmin(A("1"))
print(a.key)
print(a1.key)