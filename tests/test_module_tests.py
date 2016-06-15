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
	item = test_inst.new_vulnerability(name, description)
	assert isinstance(item, base.vulnerability)
	assert item.name() == name
	assert item.provides() == None
	assert item.version() == None


def test_valid_add_vuln():
	name = "test"
	description = "test description"

	test_inst = module_util.import_module("test_module")
	item = test_inst.new_vulnerability(name, description)

	try:
		test_inst.add_vulnerability(item)
		assert True
	except ValueError:
		assert False

	test_inst.clear_vulnerabilities()

def test_invalid_add_vuln():
	name = "test"
	description = "test description"

	test_inst = module_util.import_module("test_module")
	item = test_inst.new_vulnerability(name, description)

	try:
		test_inst.add_vulnerability({})
		assert False
	except ValueError:
		assert True

	try:
		test_inst.add_vulnerability([])
		assert False
	except ValueError:
		assert True

	try:
		test_inst.add_vulnerability("hi")
		assert False
	except ValueError:
		assert True

	try:
		test_inst.add_vulnerability(1)
		assert False
	except ValueError:

		assert True




	test_inst.clear_vulnerabilities()


def test_get_vuln_object():
	name = "test"
	description = "test description"

	test_inst = module_util.import_module("test_module")
	item = test_inst.new_vulnerability(name, description)
	test_inst.add_vulnerability(item)

	test_item = test_inst.get_vulnerability_object("test")

	assert isinstance(test_item, base.vulnerability)
	assert test_item.name() == name
	assert test_item.description() == description
	assert test_item.provides() == None
	assert test_item.version() == None

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

def test_valid_has_provides():
	name = "test"
	description = "test description"
	provides = "test"

	test_inst = module_util.import_module("test_module")
	item = test_inst.new_vulnerability(name, description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	assert test_inst.has_provides(provides) == True
	assert test_inst.has_provides("another") == False

def test_valid_has_difficulty():
	name = "test"
	description = "test description"
	provides = "test"

	test_inst = module_util.import_module("test_module")
	item = test_inst.new_vulnerability(name, description, provides, "1.0.0")
	item.set_difficulty("easy")
	test_inst.add_vulnerability(item)

	assert test_inst.has_difficulty("easy") == True
	assert test_inst.has_difficulty("hard") == True

	test_inst.clear_vulnerabilities()

	item = test_inst.new_vulnerability(name, description, provides, "1.0.0")
	item.set_difficulty("hard")
	test_inst.add_vulnerability(item)

	assert test_inst.has_difficulty("easy") == False
	assert test_inst.has_difficulty("hard") == True

def test_valid_internal():
	name = "test"
	description = "test description"
	provides = "test"

	test_inst = module_util.import_module("test_module")
	item = test_inst.new_vulnerability(name, description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	vuln_list = test_inst.get_vulnerabilities()
	test_list = test_inst.get_running_vulns()

	for i in range(len(vuln_list)):
		if not vuln_list[i].name() == test_list[i].name():
			assert False


def test_one_vuln():
	name = "test"
	description = "test description"
	provides = "test"

	test_inst = module_util.import_module("test_module")
	item = test_inst.new_vulnerability(name, description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	item = test_inst.new_vulnerability(name + "2", description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	count2 = 0

	for i in range(70):
		vuln_list = test_inst.get_vulnerabilities(force=True)

		assert len(vuln_list) == 1 or len(vuln_list) == 2
		if len(vuln_list) == 2:
			count2 += 1

		assert (vuln_list[0].name() == name or vuln_list[0].name() == name + "2")
	assert count2 == 0

def test_multi_vuln():
	name = "test"
	description = "test description"
	provides = "test"

	test_inst = module_util.import_module("test_module")
	item = test_inst.new_vulnerability(name, description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	item = test_inst.new_vulnerability(name + "2", description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	test_inst.set_multi_vuln(True)

	count2 = 0

	for i in range(70):
		vuln_list = test_inst.get_vulnerabilities(force=True)

		assert len(vuln_list) == 1 or len(vuln_list) == 2
		if len(vuln_list) == 2:
			count2 += 1

		assert (vuln_list[0].name() == name or vuln_list[0].name() == name + "2")
	assert count2 > 0

def test_NONE_vuln():
	name = "test"
	description = "test description"
	provides = "test"

	test_inst = module_util.import_module("test_module")
	item = test_inst.new_vulnerability(name, description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	item = test_inst.new_vulnerability("NONE", description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	test_inst.set_multi_vuln(True)

	for i in range(50):
		vuln_list = test_inst.get_vulnerabilities(force=True)

		assert len(vuln_list) == 1
		assert (vuln_list[0].name() == name or vuln_list[0].name() == "NONE")

def test_forced_vulns_valid():
	name = "forced"
	description = "test description"
	provides = "test"

	test_inst = module_util.import_module("test_module")
	item = test_inst.new_vulnerability(name, description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	item = test_inst.new_vulnerability("notforced", description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	test_inst.set_forced([name])


	for i in range(70):
		vuln_list = test_inst.get_vulnerabilities(force=True)

		assert len(vuln_list) == 1

		present = False

		for vuln in vuln_list:
			if vuln.name() == name:
				present = True

		assert present == True




def test_forced_vulns_valid_multi():
	name = "forced"
	description = "test description"
	provides = "test"

	test_inst = module_util.import_module("test_module")
	item = test_inst.new_vulnerability(name, description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	item = test_inst.new_vulnerability("notforced", description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	test_inst.set_forced([name])
	test_inst.set_multi_vuln(True)

	onecount = 0
	twocount = 0

	for i in range(70):
		vuln_list = test_inst.get_vulnerabilities(force=True)

		present = False

		for vuln in vuln_list:
			if vuln.name() == name:
				present = True

		assert present == True

		if len(vuln_list) == 1:
			onecount += 1
		elif len(vuln_list) == 2:
			twocount += 1
		else:
			assert False

	assert onecount > 0
	assert twocount > 0



def test_forced_vulns_valid_multiple_forced():
	name = "forced"
	name2 = "alsoforced"
	description = "test description"
	provides = "test"

	test_inst = module_util.import_module("test_module")
	item = test_inst.new_vulnerability(name, description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	item = test_inst.new_vulnerability(name2, description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	firstcount = 0
	secondcount = 0

	for i in range(70):

		test_inst.set_forced([name, name2])

		vuln_list = test_inst.get_vulnerabilities(force=True)

		assert len(vuln_list) == 1

		present = False
		vuln = vuln_list[0]

		assert vuln.name() == name or vuln.name() == name2

		if vuln.name() == name:
			firstcount += 1
		elif vuln.name() == name2:
			secondcount += 1
		else:
			assert False

	assert firstcount > 0
	assert secondcount > 0


def test_forced_vulns_valid_multi_forced_multi():
	name = "forced"
	name2 = "alsoforced"
	description = "test description"
	provides = "test"

	test_inst = module_util.import_module("test_module")
	item = test_inst.new_vulnerability(name, description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	item = test_inst.new_vulnerability("notforced", description, provides, "1.0.0")
	test_inst.add_vulnerability(item)

	item = test_inst.new_vulnerability(name2, description, provides, "1.0.0")
	test_inst.add_vulnerability(item)


	test_inst.set_multi_vuln(True)
	test_inst.set_forced([name, name2])

	for i in range(70):
		vuln_list = test_inst.get_vulnerabilities(force=True)

		present = False

		for vuln in vuln_list:
			if vuln.name() == name:
				present = True

		assert present == True

		present = False

		for vuln in vuln_list:
			if vuln.name() == name2:
				present = True

		assert present == True

def test_storage_file():
	test_inst = module_util.import_module("test_module")
	sfile = test_inst.storage_file("test_file")
	assert sfile.get_contents().strip() == "This is data"

def test_invalid_storage_file():
	test_inst = module_util.import_module("test_module")
	try:
		sfile = test_inst.storage_file("doesnt_exist")
		assert False
	except:
		assert True
