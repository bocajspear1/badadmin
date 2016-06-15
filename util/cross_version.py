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
# @returns int - Value of major Python version
#
def get_python_version():
	return sys.version_info[0]

##
# Cross-version test to see if value is a string
#
# @param string (object) - Value to test if it is a string
# @returns bool
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
# @param value (object) - Value to test if it is an integer
# @returns bool
#
def isinteger(value):

	python_version = get_python_version()

	if python_version == 3:
		return isinstance( value, int )
	elif python_version == 2:
		return isinstance( value, ( int, long ) )
	else:
		print("Invalid python version")

##
# Cross-version test to see if value is a string with an integer (no decimal), or an integer
#
# @param value (object) - Value to test
# @returns bool
#
def isnumeric(value):
	python_version = get_python_version()

	if isinteger(value):
		return True

	if python_version == 3:
		try:
			return value.isnumeric()
		except AttributeError:
			return False
	elif python_version == 2:
		value = unicode(value)
		return value.isnumeric()
	else:
		print("Invalid python version")

## Cross version enum. Created with a list, for example: test_enum = cross_version.Enum(['a','b', 'c'])
#
class Enum(frozenset):
## @cond HIDDEN
	def __getattr__(self, name):
		if name in self:
			return copy.deepcopy(name)

	def __setattr__(self, name, value):
		raise AttributeError("Cannot modify value in Enum")

## @endcond
