import sys
import os
from pprint import pprint
import importlib

#sys.path.append("./modules")

def test_module_path():
	if not os.path.exists("./modules/test_module") or not os.path.exists("./modules/test_module/test_module.py"):
		assert False

def test_module_import():
	temp = importlib.import_module("modules.test_module.test_module")
		
	module_class = getattr(temp, "test_module")

	test_obj = module_class()
	assert isinstance(test_obj, module_class)

def test_basic_module_info():
	temp = importlib.import_module("modules.test_module.test_module")
		
	test_obj = getattr(temp, "test_module")()
	
	assert test_obj.name() == "Test Module"
	assert test_obj.version() == "1.0.0"
	assert test_obj.author() == "Test Author"
