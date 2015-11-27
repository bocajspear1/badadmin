#import importlib
import os
import util.cross_version
import modules.base as base
import copy 

stub_map = {}

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
		return False

def module_exists(module_name):
	if not util.cross_version.isstring(module_name):
		return False
		
	if module_name in stub_map:
		return True
	elif not os.path.exists("./modules/" + module_name) or not os.path.exists("./modules/" + module_name + "/" + module_name + ".py"):
		return False
	else:
		return True

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

def set_stub_module(module_name, module_object):
	if module_exists(module_name):
		print("Overridding " + module_name)
	
	if not issubclass(module_object.__class__, base.module_base):
		raise ValueError("Stub module object must be a subclass of module_base")
		
	stub_map[module_name] = module_object
	
def remove_stub_module(module_name):
	if module_name in stub_map:
		del stub_map[module_name]

def get_stubs():
	return copy.deepcopy(stub_map)
