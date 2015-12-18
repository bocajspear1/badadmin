# This unit tests basic module functionality using the test module
import sys
import os
from util.ba_random import ba_random

from pprint import pprint
#~ import importlib

#sys.path.append("./modules")

def test_random_number():
	obj = ba_random()
	for i in range(400):
		num = obj.random_number(0, 10)
		assert num >= 0 and num <= 10

def test_random_array():
	obj = ba_random()
	l = [1,2,3,4,5]
	for i in range(400):
		val = obj.array_random(l)
		assert val in l
		assert val == 1 or val == 2 or val == 3 or val == 4 or val == 5


def test_random_string():
	obj = ba_random()
	for i in range(400):
		val = obj.random_string(2, 10)
		assert len(val) >= 2 and len(val) <= 10

def test_will_do():
	obj = ba_random()
	truecount = 0
	falsecount = 0
	for i in range(400):
		val = obj.will_do()
		assert val == True or val == False
		
		if val == True:
			truecount += 1
		elif val == False:
			falsecount += 1
	
	assert truecount > 0
	assert falsecount > 0
