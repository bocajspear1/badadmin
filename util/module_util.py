import importlib
import os
import util.cross_version

def import_module(module_name):
	
	if not util.cross_version.isstring(module_name):
		return False
	
	if not os.path.exists("./modules/" + module_name) or not os.path.exists("./modules/" + module_name + "/" + module_name + ".py"):
		return False
	else:
		temp = importlib.import_module("modules." + module_name + "." + module_name)
			
		module_class = getattr(temp, module_name)

		return module_class()
