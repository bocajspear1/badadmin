## @package util.cross_version
#
# Cross-version functions
#
# Since BadAdmin attempts to run across both Python 2 and 3, some similar functions that 
# would be different the two version are provided here
#
import sys
import copy


## 
# Returns the major version of the running Python
#
# @returns Integer - Value of major Python version
#
def get_python_version():
	return sys.version_info[0]

## 
# Cross-version test to see if value is a string
#
# @param object string - Value to test if it is a string
# @returns Boolean
#
def isstring(string):
	
	python_version = get_python_version()
	
	if python_version == 3:
		return isinstance(string, str)
	elif python_version == 2:
		return isinstance(string, basestring)
	else:
		print("Invalid python version")

## 
# Cross-version test to see if value is an integer (no decimal)
#
# @param object value - Value to test if it is an integer
# @returns Boolean
#
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

