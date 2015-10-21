import importlib
import os
import util.cross_version

def import_module(module_name):
	
	if module_exists(module_name):
		temp = importlib.import_module("modules." + module_name + "." + module_name)
			
		module_class = getattr(temp, module_name)

		return module_class()
	else:
		return False

def module_exists(module_name):
	if not util.cross_version.isstring(module_name):
		return False
	
	if not os.path.exists("./modules/" + module_name) or not os.path.exists("./modules/" + module_name + "/" + module_name + ".py"):
		return False
	else:
		return True

def list_modules():
	dir_list = os.listdir("./modules/")
	
	ret_list = []
	
	for item in dir_list:
		if not ".py" in item:
			if module_exists(item):
				ret_list.append(item)
	
	return ret_list
