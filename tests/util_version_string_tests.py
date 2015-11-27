import sys
import os

import util.version_util as version_util

def test_version():
	
	test = version_util.version("1.0a")
	assert test.get_tuple() == (1,0,'a')
	
	test = version_util.version("1.0.1")
	assert test.get_tuple() == (1,0, '',1, '')
	
	test = version_util.version("5.9.0.1beta")
	assert test.get_tuple() == (5,9, '',0, '', 1, 'beta')
	
	
def test_invalid_version():
	
	try:
		test = version_util.version("1.0.0.0.0.0")
		assert False
	except ValueError:
		assert True
		
	try:
		test = version_util.version("1.0,0")
		assert False
	except ValueError:
		assert True
		
	try:
		test = version_util.version("a.b.c")
		assert False
	except ValueError:
		assert True

	try:
		test = version_util.version("1.0.0")
		
		test == "abc"
		
		assert False
	except ValueError:
		assert True

def test_invalid_range():
	try:
		test = version_util.version_range(">a.b")
		assert False
	except ValueError:
		assert True
		
	try:
		test = version_util.version("-012")
		assert False
	except ValueError:
		assert True
		
	try:
		test = version_util.version("<=>1.0.0")
		assert False
	except ValueError:
		assert True
	

def test_test_range():

	test_range = version_util.version_range(">1.0.1")
	
	assert test_range.in_range("1.0.0") == False
	assert test_range.in_range("1.0.3") == True
	assert test_range.in_range("0.0.4") == False
	assert test_range.in_range("0.4") == False
	assert test_range.in_range("4") == True
	
	test_range = version_util.version_range("<=4.5.0.1")
	
	assert test_range.in_range("4.5.0.1") == True
	assert test_range.in_range("4.5.0.1-a") == True
	assert test_range.in_range("1.0.3") == True
	assert test_range.in_range("0.0.4") == True
	assert test_range.in_range("4.6") == False
	assert test_range.in_range("4.7.8.9") == False
	
	
	test_range = version_util.version_range(">=3.4.1a")
	
	assert test_range.in_range("4.5.0.1") == True
	assert test_range.in_range("3.4.2") == True
	assert test_range.in_range("3.4.1b") == True
	assert test_range.in_range("5.6.7.6b") == True
	assert test_range.in_range("3.3") == False
	assert test_range.in_range("3.4.1") == False
	
	
	test_range = version_util.version_range("=20.0.1")
	
	assert test_range.in_range("20.0.1") == True
	assert test_range.in_range("20.0.1a") == False
	assert test_range.in_range("1.0.3") == False
	assert test_range.in_range("0.0.4") == False
	assert test_range.in_range("4.6") == False
	assert test_range.in_range("4.7.8.9") == False
	

	
	
