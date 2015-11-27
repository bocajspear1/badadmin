## @package util.cross_version
# Functions for functionality between Python 2 and Python 3
import sys
import copy


def get_python_version():
	return sys.version_info[0]

## 
# Cross-version test to see if value is a string
#
# @param string string - Value to test if string
#
def isstring(string):
	
	python_version = get_python_version()
	
	if python_version == 3:
		return isinstance(string, str)
	elif python_version == 2:
		return isinstance(string, basestring)
	else:
		print("Invalid python version")

def isinteger(value):
	
	python_version = get_python_version()
	
	if python_version == 3:
		return isinstance( value, int )
	elif python_version == 2:
		return isinstance( value, ( int, long ) )
	else:
		print("Invalid python version")
	
	

class Enum(frozenset):
	def __getattr__(self, name):
		if name in self:
			return copy.deepcopy(name)
		
	def __setattr__(self, name, value):
		raise AttributeError("Cannot modify value in Enum")

