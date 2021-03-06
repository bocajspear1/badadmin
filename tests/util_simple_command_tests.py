# Test file for base.py file

# Insert the module into the path

import sys
import os
sys.path.append("./modules") 

from util.simple_command import simple_command


def test_single_command():
	returncode, return_list, error_list = simple_command().run("ls /")
	
	
	assert returncode == 0
	assert len(return_list) >= 1
	assert len(error_list) == 0
	assert 'root' in return_list
	assert 'bin' in return_list

def test_single_command_extra():
	returncode, return_list, error_list = simple_command().run("cat", ["stuff", 'not','exist'])
	
	assert returncode == 0
	assert len(return_list) >= 1
	assert len(error_list) == 0
	assert "stuff" in return_list
	assert 'not' in return_list
	assert not 'cat' in return_list
	assert 'exist' in return_list

def test_invalid_command():
	returncode, return_list, error_list = simple_command().run("non-existant")

	assert returncode != 0
	assert len(return_list) == 0
	assert len(error_list) >= 1
	assert 'not found' in error_list[0]

def test_non_string_command():
	try:
		returncode, return_list, error_list = simple_command().run({"stuff": "stuff"})
		assert False
	except ValueError:
		assert True
	
