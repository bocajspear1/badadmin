# This unit tests basic module functionality using the test module
import sys
import os
import util.module_util as module_util
import modules.base as base

#~ import importlib

#sys.path.append("./modules")

def test_module_path():
	if not os.path.exists("./modules/test_module") or not os.path.exists("./modules/test_module/test_module.py"):
		assert False

def test_module_import():
	#~ temp = importlib.import_module("modules.test_module.test_module")
	temp = __import__("modules.test_module.test_module",globals(), locals(), ['./modules'],0)
	
	module_class = getattr(temp, "test_module")

	test_obj = module_class()
	
	test_obj2 = module_util.import_module("test_module")
	
	assert isinstance(test_obj, module_class)
	assert isinstance(test_obj2, module_class)

def test_basic_module_info():
	#~ temp = importlib.import_module("modules.test_module.test_module")
	
	temp = __import__("modules.test_module.test_module",globals(), locals(), ['./modules'],0)
	
	test_obj = getattr(temp, "test_module")()
	
	assert test_obj.name() == "Test Module"
	assert test_obj.version() == "1.0.0"
	assert test_obj.author() == "Test Author"
	assert test_obj.description() == "Test Description"
	
def test_module_name():
	test_inst = module_util.import_module("test_module")
	assert test_inst.get_class_name() == "test_module"

def test_new_vuln():
	name = "test"
	description = "test description"
	
	test_inst = module_util.import_module("test_module")
	item = test_inst._new_vulnerability(name, description)
	assert isinstance(item, base.vulnerability)
	assert item.get_name() == name
	assert item.get_provides() == None
	assert item.get_version() == None
	

def test_valid_add_vuln():
	name = "test"
	description = "test description"
	
	test_inst = module_util.import_module("test_module")
	item = test_inst._new_vulnerability(name, description)
	
	try:
		test_inst._add_vulnerability(item)
		assert True
	except ValueError:
		assert False

	test_inst._clear_vulnerabilities()

def test_invalid_add_vuln():
	name = "test"
	description = "test description"
	
	test_inst = module_util.import_module("test_module")
	item = test_inst._new_vulnerability(name, description)
	
	try:
		test_inst._add_vulnerability({})
		assert False
	except ValueError:
		assert True

	try:
		test_inst._add_vulnerability([])
		assert False
	except ValueError:
		assert True

	try:
		test_inst._add_vulnerability("hi")
		assert False
	except ValueError:
		assert True

	try:
		test_inst._add_vulnerability(1)
		assert False
	except ValueError:
		
		assert True




	test_inst._clear_vulnerabilities()


def test_get_vuln_object():
	name = "test"
	description = "test description"
	
	test_inst = module_util.import_module("test_module")
	item = test_inst._new_vulnerability(name, description)
	test_inst._add_vulnerability(item)
	
	test_item = test_inst.get_vulnerability_object("test")
	
	assert isinstance(test_item, base.vulnerability)
	assert test_item.get_name() == name
	assert test_item.get_description() == description
	assert test_item.get_provides() == None
	assert test_item.get_version() == None

def test_set_multi_valid():
	name = "test"
	description = "test description"
	
	test_inst = module_util.import_module("test_module")
	try:
		test_inst.set_multi_vuln(True)
		assert True
	except ValueError:
		assert False

	try:
		test_inst.set_multi_vuln(False)
		assert True
	except ValueError:
		assert False
		
def test_set_multi_invalid():
	name = "test"
	description = "test description"
	
	test_inst = module_util.import_module("test_module")
	try:
		test_inst.set_multi_vuln('a')
		assert False
	except ValueError:
		assert True

	try:
		test_inst.set_multi_vuln([])
		assert False
	except ValueError:
		assert True


