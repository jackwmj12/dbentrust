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
class NaN:
	def __str__(self):
		return "NaN"
	
	def __repr__(self):
		return "NaN"
	
	def __gt__(self, other):
		if not isinstance(other, int):
			raise TypeError(" > 运算对象是int")
		return False
	
	def __lt__(self, other):
		if not isinstance(other, int):
			raise TypeError(" < 运算对象是int")
		return True
	
	def __ge__(self, other):
		if not isinstance(other, int):
			raise TypeError(" >= 运算对象是int")
		return False
	
	def __le__(self, other):
		if not isinstance(other, int):
			raise TypeError(" <= 运算对象是int")
		return True
	
	def __add__(self, other):
		if not isinstance(other, int):
			raise TypeError(" + 运算对象是int")
		return 0 + other
	
	def __radd__(self, other):
		if not isinstance(other, int):
			raise TypeError(" + 运算对象是int")
		return 0 + other
	
	def __sub__(self, other):
		if not isinstance(other, int):
			raise TypeError(" - 运算对象是int")
		return 0 - other
	
	def __rsub__(self, other):
		if not isinstance(other, int):
			raise TypeError(" - 运算对象是int")
		return other
	
	def __int__(self):
		return 0
	
	def __float__(self):
		return 0.0
	
	def __eq__(self, other):
		if isinstance(other, str) and other == "NaN":
			return True
		elif isinstance(other, NaN):
			return True
		return False

class Number:
	NaN = NaN()
	
	def __int__(self, number):
		if number == self.NaN:
			return NaN()
		return number
	
	@classmethod
	def checkNaN(cls, number):
		if number == cls.NaN:
			return True
		return False
	
	@classmethod
	def getInt(cls, number):
		if cls.checkNaN(number):
			return cls.NaN
		return int(number)
	
	@classmethod
	def getFloat(cls, number):
		if cls.checkNaN(number):
			return cls.NaN
		return int(number)

__all__ = ["Number"]

if __name__ == '__main__':
	a = Number.NaN
	print(int(a))
	# print(type(a))