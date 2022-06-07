# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : number.py
# @Time     : 2021-04-29 15:12
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
from loguru import logger

from dbentrust.utils.singleton import Singleton


def isNum(inputNum):
	if isinstance(inputNum, int) or isinstance(inputNum, float):
		return True
	return False

class __NaN__(metaclass=Singleton):

	def __str__(self):
		return "NaN"
	
	def __repr__(self):
		return "NaN"

	def __format__(self, format_spec):
		return "NaN"

	def __gt__(self, other):
		if isinstance(other,__NaN__):
			return False
		elif not isNum(other):
			raise TypeError(" > 运算对象是 (int,NaN,float) ")
		return False
	
	def __lt__(self, other):
		if isinstance(other,__NaN__):
			return False
		elif not isNum(other):
			raise TypeError(" < 运算对象是 (int,NaN,float) ")
		return True
	
	def __ge__(self, other):
		if isinstance(other,__NaN__):
			return True
		elif not isNum(other):
			raise TypeError(" >= 运算对象是 (int,NaN,float) ")
		return False
	
	def __le__(self, other):
		if isinstance(other,__NaN__):
			return True
		if not isNum(other):
			raise TypeError(" <= 运算对象是 (int,NaN,float) ")
		return True
	
	def __add__(self, other):
		if isinstance(other,__NaN__):
			other = 0
		if not isNum(other):
			raise TypeError(" + 运算对象是 (int,NaN,float) ")
		return 0 + other
	
	def __radd__(self, other):
		if isinstance(other,__NaN__):
			other = 0
		if not isNum(other):
			raise TypeError(" + 运算对象是 (int,NaN,float) ")
		return 0 + other
	
	def __sub__(self, other):
		if isinstance(other,__NaN__):
			other = 0
		elif not isNum(other):
			raise TypeError(" - 运算对象是 (int,NaN,float) ")
		return 0 - other
	
	def __rsub__(self, other):
		if isinstance(other,__NaN__):
			other = 0
		elif not isNum(other):
			raise TypeError(" - 运算对象是 (int,NaN,float) ")
		return other
	
	def __mul__(self, other):
		return 0
	
	def __rmul__(self, other):
		return 0
	
	def __floordiv__(self, other):
		if other == 0 :
			raise TypeError(" 0 无法被除")
		elif not isNum(other):
			raise TypeError(" / 运算对象是 (int,NaN,float) ")
		return 0
	
	def __mod__(self,other):
		if other == 0 :
			raise TypeError(" 0 无法被除")
		elif not isNum(other):
			raise TypeError(" / 运算对象是 (int,NaN,float) ")
		return 0
	
	def __divmod__(self, other):
		if other == 0 :
			raise TypeError(" 0 无法被除")
		elif not isNum(other):
			raise TypeError(" / 运算对象是 (int,NaN,float) ")
		return 0
	
	def __truediv__(self, other):
		return 0
	
	def __int__(self):
		return 0

	def __float__(self):
		return 0.0

	def __eq__(self, other):
		if isinstance(other, str) and other == "NaN":
			return True
		elif isinstance(other, __NaN__):
			return True
		return False

NaN = __NaN__()

def checkNaN(number):
	if number == NaN:
		return True
	return False

def isNaN(number):
	if number == NaN:
		return True
	return False

def getInt(number):
	if checkNaN(number):
		return NaN
	return int(number)

def getFloat(number):
	if checkNaN(number):
		return NaN
	return float(number)

def get_int(number):
	if checkNaN(number):
		return 0
	return int(number)

def get_float(number):
	if checkNaN(number):
		return 0
	return float(number)

class Number:

	def __int__(self, number):
		if number == NaN:
			return NaN
		return number

__all__ = ["isNum","NaN","Number","checkNaN","isNaN","getInt","getFloat","get_int","get_float"]

if __name__ == '__main__':
	a = NaN
	b = NaN
	# NaN = "a"

	# b = __NaN__()

	# logger.debug(id(a))
	# logger.debug(id(b))
	# logger.debug(id(NaN))

	logger.debug(b > 1)
	logger.debug(1 > b)
	logger.debug(a > b)
	logger.debug(a//1)
	logger.debug(a%1)
	logger.debug(divmod(a,1))
	logger.debug(int(a))
	logger.debug(type(a))
	logger.debug(checkNaN("NaN"))
	logger.debug(getInt("NaN"))
	logger.debug(get_int("NaN"))
	logger.debug(getFloat("NaN"))
	logger.debug(get_float("NaN"))
