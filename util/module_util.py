## @package util.module_util
# 
# Python module for importing, listing and manipulating BadAdmin modules
#
# Also manages stub modules. Stub modules are instances of module classes
# that do not actually exist as files, or override existing modules. 
# These are usually used for testing.
#
import os
import util.cross_version
import modules.base as base
import copy 

## Maps a name to a stub module
stub_map = {}

## Imports a module given by name
#
# @param module_name (string) - The name of the module
# @returns None or module object
#
def import_module(module_name):
	
	if module_exists(module_name):
		if module_name in stub_map:
			return stub_map[module_name]
		else:
			#~ temp = importlib.import_module("modules." + module_name + "." + module_name)
			temp = temp = __import__("modules." + module_name + "." + module_name,globals(), locals(), ['./modules'],0)
				
			module_class = getattr(temp, module_name)

			return module_class()
	else:
		return None

## Checks if a module exists and all files are properly
#
# @param module_name (string) - The name of the module
# @returns bool
#
def module_exists(module_name):
	if not util.cross_version.isstring(module_name):
		return False
		
	if module_name in stub_map:
		return True
	elif not os.path.exists("./modules/" + module_name) or not os.path.exists("./modules/" + module_name + "/" + module_name + ".py"):
		return False
	else:
		return True

## Returns a list of known modules
#
# Modules are stored in the modules/ directory in the root BadAdmin directory
# Also includes stub modules
#
# @returns string[]
#
def get_module_list():
	dir_list = os.listdir("./modules/")
	
	ret_list = []
	
	for item in dir_list:
		if not ".py" in item:
			if module_exists(item):
				ret_list.append(item)
	
	for item in stub_map:
		ret_list.append(item)
	
	return ret_list

## Set a stub module to respond for a given module name
#
# This can override existing modules
#
# @param module_name (string) - Name the stub module will respond for
# @param module_object (object) - Object (subclass of module_base) that will act as the module
#
def set_stub_module(module_name, module_object):
	if module_exists(module_name):
		print("Overridding " + module_name)
	
	if not issubclass(module_object.__class__, base.module_base):
		raise ValueError("Stub module object must be a subclass of module_base")
		
	stub_map[module_name] = module_object

## Removes a stub module
#
# @param module_name (string) - Name of the stub module that will be removed
#	
def remove_stub_module(module_name):
	if module_name in stub_map:
		del stub_map[module_name]

## Returns a copy of the stub mappings
#
# @returns dict - 'key' = module name, 'value' = module object
#
def get_stubs():
	return copy.deepcopy(stub_map)
