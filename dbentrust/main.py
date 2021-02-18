# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : main.py
# @Time     : 2021-02-18 19:10
# @Software : tiseal_app
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


def installTxRedis():
	redisModule.install("txredisapi")

def installAioRedis():
	redisModule.install("aioredis")

def installRedis():
	redisModule.install("redis")

class redisModule():
	name = ""

	@classmethod
	def install(cls,name= "txredisapi"):
		cls.name = name