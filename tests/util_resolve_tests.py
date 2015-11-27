# This unit tests basic module functionality using the test module
import sys
import os
import util.module_util as module_util
import util.resolve as resolve
import modules.base as base


added_stub_modules = []

def generate_modules(config):
	for item in config:
		
		new_module = module_util.import_module("test_module")
		
		if not "class_name" in item:
			raise ValueError("class_name is required")
		elif not "print_name" in item:
			raise ValueError("print_name is required")
		
		
		new_module.override_class_name(item['class_name'])
		new_module.set_name(item['print_name'])
		
		assert new_module.get_class_name() == item['class_name']
		assert new_module.name() == item['print_name']
		
		for vuln in item['vulns']:
			
			new_vuln = new_module._new_vulnerability(vuln['name'], vuln['desc'], vuln['provides'], vuln['version'])
			
			for dep in vuln['deps']:
				new_vuln.add_dependency(dep['provides'], dep['range'])
								
			new_module._add_vulnerability(new_vuln)
		
		module_util.set_stub_module(item['class_name'], new_module)
		added_stub_modules.append(item['class_name'])
		
def remove_stubs():
	for module in added_stub_modules:
		module_util.remove_stub_module(module)


def test_set_name():
	test_obj = module_util.import_module("test_module")
	
	assert test_obj.name() == "Test Module"
	test_obj.set_name("Test_Module 2")
	assert test_obj.name() == "Test_Module 2"


	
def test_resolve_simple():
	
	mod_1 = module_util.import_module("test_module")
	
	vuln1 = mod_1._new_vulnerability("VULN_1_A", "Test Vuln A", "A", "1.0.0")
	vuln1.add_dependency("B", ">0.1")
	mod_1._add_vulnerability(vuln1)
	mod_1.override_class_name("mod_1")
	mod_1.set_name("Mod_1")
	assert mod_1.get_class_name() == "mod_1"
	
	module_util.set_stub_module("mod_1", mod_1)
	
	
	mod_2 = module_util.import_module("test_module")
	vuln2 = mod_2._new_vulnerability("VULN_2_A", "Test Vuln B", "B", "1.0.0")
	mod_2._add_vulnerability(vuln2)
	mod_2.override_class_name("mod_2")
	mod_2.set_name("Mod_2")
	
	assert mod_2.get_class_name() == "mod_2"
	
	module_util.set_stub_module("mod_2", mod_2)
	
	mod_list = module_util.get_module_list()
	
	assert "mod_1" in mod_list
	assert "mod_2" in mod_list
	

	resolving = resolve.resolver()
	resolving.add_module("mod_1")

	assert resolving.start_resolve() == True
	
	assert resolving.get_install_order() == ['mod_2', 'mod_1']
	
	resolving = resolve.resolver()
	resolving.add_module("mod_1")
	resolving.add_module("mod_2")

	assert resolving.start_resolve() == True

	assert resolving.get_install_order() == ['mod_2', 'mod_1']
	assert resolving.get_install_order() != ['mod_1', 'mod_2']
	
	module_util.remove_stub_module("mod_1")
	module_util.remove_stub_module("mod_2")
	

def test_resolve_3_layer_2():
	
	config = [
	{
		"print_name": "Mod_1",
		"class_name": "mod_1",
		"vulns": [
			{
				"name": "VULN_1_A",
				"desc": "Test Vuln 1A",
				"provides": "A",
				"version": "1.0.0",
				"deps": [
					{"provides": "B", "range": ">0.1"}
				]
			},
			{
				"name": "VULN_1_B",
				"desc": "Test Vuln 1B",
				"provides": "",
				"version": "",
				"deps": [
					{"provides": "B", "range": "=1.2.0"}
				]
			}
		]
	},
	{
		"print_name": "Mod_2",
		"class_name": "mod_2",
		"vulns": [
			{
				"name": "VULN_2_A",
				"desc": "Test Vuln 2A",
				"provides": "B",
				"version": "1.2.0",
				"deps": [
					{"provides": "C", "range": "<=10.1"}
				]
			}
		]
	},
	{
		"print_name": "Mod_3",
		"class_name": "mod_3",
		"vulns": [
			{
				"name": "VULN_3_A",
				"desc": "Test Vuln 3A",
				"provides": "C",
				"version": "4.5.0",
				"deps": [
					
				]
			}
		]
	}
	]
	
	generate_modules(config)
	
	mod_list = module_util.get_module_list()
	
	assert "mod_1" in mod_list
	assert "mod_2" in mod_list
	assert "mod_3" in mod_list

	resolving = resolve.resolver()
	resolving.add_module("mod_1")

	assert resolving.start_resolve() == True
	
	assert resolving.get_install_order() == ['mod_3', 'mod_2', 'mod_1']
	
	resolving = resolve.resolver()
	resolving.add_module("mod_1")
	resolving.add_module("mod_3")
	
	assert resolving.start_resolve() == True

	assert resolving.get_install_order() == ['mod_3','mod_2', 'mod_1']
	
	remove_stubs()

def test_invalid():
	
	config = [
	{
		"print_name": "Mod_1",
		"class_name": "mod_1",
		"vulns": [
			{
				"name": "VULN_1_A",
				"desc": "Test Vuln 1A",
				"provides": "A",
				"version": "1.0.0",
				"deps": [
					{"provides": "Z", "range": ">2.0.0"}
				]
			}
		]
	},
	{
		"print_name": "Mod_2",
		"class_name": "mod_2",
		"vulns": [
			{
				"name": "VULN_2_A",
				"desc": "Test Vuln 2A",
				"provides": "B",
				"version": "1.2.0",
				"deps": [
					
				]
			}
		]
	}
	]
	
	generate_modules(config)
	
	mod_list = module_util.get_module_list()
	
	assert "mod_1" in mod_list
	assert "mod_2" in mod_list

	resolving = resolve.resolver()
	resolving.add_module("mod_1")

	assert resolving.start_resolve() == False
	
	resolving = resolve.resolver()
	resolving.add_module("mod_1")
	resolving.add_module("mod_2")
	
	assert resolving.start_resolve() == False

	
	remove_stubs()

def test_invalid_2():
	
	config = [
	{
		"print_name": "Mod_1",
		"class_name": "mod_1",
		"vulns": [
			{
				"name": "VULN_1_A",
				"desc": "Test Vuln 1A",
				"provides": "A",
				"version": "1.0.0",
				"deps": [
					{"provides": "B", "range": ">2.0.0"}
				]
			}
		]
	},
	{
		"print_name": "Mod_2",
		"class_name": "mod_2",
		"vulns": [
			{
				"name": "VULN_2_A",
				"desc": "Test Vuln 2A",
				"provides": "B",
				"version": "1.2.0",
				"deps": [
					
				]
			}
		]
	}
	]
	
	generate_modules(config)
	
	mod_list = module_util.get_module_list()
	
	assert "mod_1" in mod_list
	assert "mod_2" in mod_list

	resolving = resolve.resolver()
	resolving.add_module("mod_1")

	assert resolving.start_resolve() == False
	
	resolving = resolve.resolver()
	resolving.add_module("mod_1")
	resolving.add_module("mod_2")
	
	assert resolving.start_resolve() == False

	
	remove_stubs()
	
def test_resolve_3_layer_2():
	
	config = [
	{
		"print_name": "Mod_1",
		"class_name": "mod_1",
		"vulns": [
			{
				"name": "VULN_1_A",
				"desc": "Test Vuln 1A",
				"provides": "A",
				"version": "1.0.0",
				"deps": [
					{"provides": "B", "range": ">0.1"}
				]
			},
			{
				"name": "VULN_1_B",
				"desc": "Test Vuln 1B",
				"provides": "",
				"version": "",
				"deps": [
					{"provides": "B", "range": "=1.2.0"}
				]
			}
		]
	},
	{
		"print_name": "Mod_2",
		"class_name": "mod_2",
		"vulns": [
			{
				"name": "VULN_2_A",
				"desc": "Test Vuln 2A",
				"provides": "B",
				"version": "1.2.0",
				"deps": [
					{"provides": "C", "range": "<=10.1"}
				]
			}
		]
	},
	{
		"print_name": "Mod_3",
		"class_name": "mod_3",
		"vulns": [
			{
				"name": "VULN_3_A",
				"desc": "Test Vuln 3A",
				"provides": "C",
				"version": "4.5.0",
				"deps": [
					
				]
			}
		]
	}
	]
	
	generate_modules(config)
	
	mod_list = module_util.get_module_list()
	
	assert "mod_1" in mod_list
	assert "mod_2" in mod_list
	assert "mod_3" in mod_list

	resolving = resolve.resolver()
	resolving.add_module("mod_1")

	assert resolving.start_resolve() == True
	
	assert resolving.get_install_order() == ['mod_3', 'mod_2', 'mod_1']
	
	resolving = resolve.resolver()
	resolving.add_module("mod_1")
	resolving.add_module("mod_3")
	
	assert resolving.start_resolve() == True

	assert resolving.get_install_order() == ['mod_3','mod_2', 'mod_1']
	
	remove_stubs()
