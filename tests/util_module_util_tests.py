# This unit tests basic module functionality using the test module
import sys
import os
import util.module_util as module_util

from pprint import pprint
#~ import importlib

#sys.path.append("./modules")

def test_module_path():
	if not os.path.exists("./modules/test_module") or not os.path.exists("./modules/test_module/test_module.py"):
		assert False

def test_module_exists():

	assert module_util.module_exists("test_module")

def test_module_import():
	test_obj = module_util.import_module("test_module")

	assert test_obj.name() == "Test Module"
	

def test_module_list():
	module_list = module_util.get_module_list()
	
	assert "test_module" in module_list

def test_set_stub_module():
	
	test_obj = module_util.import_module("test_module")
	
	test_obj.override_class_name("test2")
	
	assert test_obj.get_class_name() == "test2"
	
	test_obj.set_name("test2")
	
	assert test_obj.name() == "test2"
	
	module_util.set_stub_module("test2", test_obj)
	
	assert module_util.module_exists("test2")
	module_list = module_util.get_module_list()
	assert "test2" in module_list

	module_util.remove_stub_module("test2")
	
	assert not module_util.module_exists("test2")
	module_list = module_util.get_module_list()
	assert not "test2" in module_list
