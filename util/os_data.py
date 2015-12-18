## @package util.os_data
#
# This module provides easy access to basic OS type information
#
# OS identification revolves around three main values:
# * OS type - The type of operating system, such as Linux or Windows
# * OS flavor - The release or distribution of the OS type, such as Ubuntu or Windows 7
# * OS version - A particular version of the OS flavor, such as Ubuntu 12.04 and Windows 7 Service Pack 1
#
import sys
import platform
import copy
from util.cross_version import Enum
import util.version_util as version_util

## List of valid operating system strings and os type strings
_os_list = {
	'linux': [
		'debian',
		'centos', 
		#'SUSE',
		'ubuntu',  
	],
	'windows': [
		'win_7',
		'win_8',
		'win_8_1',
		'win_server_2003', 
		'win_server_2008',
		'win_server_2012',
		'win_xp',
		'win_9x', 
		#'REACTOS',
	]
	
}

## Checks if the given string is a valid os_type value
#
# @param string os_type - String to test
# @returns Boolean
#
def valid_os(os_type):
	if os_type in _os_list:
		return True
	else:
		return False

## Checks if the given string is a valid flavor for the given OS type
#
# @param string os_type - To OS type of the flavor
# @param string flavor - The flavor value to test
# @returns Boolean
#	
def valid_flavor(os_type, flavor):
	if not valid_os(os_type):
		return False
	
	if flavor in _os_list[os_type]:
		return True
		
	return False

# Inline functions used to make sure I don't misspell anything :)

# @cond HIDDEN
def validate_os(os_type):
	if valid_os(os_type):
		return os_type
	else:
		raise ValueError("Invalid os type")

def validate_flavor(os_type, flavor):
	if not valid_os(os_type):
		raise ValueError("Invalid os type")
	else:
		if valid_flavor(os_type, flavor):
			return flavor
		else:
			raise ValueError("Invalid os type")

# @endcond

## Object that represents a os match and is used in comparing the current OS, stored in 'os_info' to
# a desired os, which is stored in 'os_match'
#
# In matches, for both flavor and version_range, '*' can be used to match any value, while '-' can be used to match none
#
#
class os_match(object):
	
	## Creates a os_match object
	#
	# @param string os_type - The type of OS to match. This must be set
	# @param string flavor - The flavor or the OS type to match. Defaults to '*'
	# @param string version_range - The version range of the flavor to match. Defaults to '*'
	def __init__(self, os_type, flavor='*', version_range='*'):
		
		if valid_os(os_type):
			self.__os_type = os_type
		else:
			raise ValueError("Invalid OS type")
			
		
		if flavor == '*' or flavor == "-":
			self.__flavor = flavor
		elif valid_flavor(self.__os_type, flavor):
			self.__flavor = flavor
		else:
			raise ValueError("Invalid OS flavor")
			
			
		self.__version = version_util.version_range(version_range)
	
	## Retrieves the flavor
	#
	# @returns string - The flavor to match
	#
	def flavor(self):
		return copy.deepcopy(self.__flavor)
	
	## Retrieves the OS type
	#
	# @returns string - The OS type to match
	#
	def os_type(self):
		return copy.deepcopy(self.__os_type)
	
	## Retrieves the version range
	#
	# @returns string - The version range to match
	#
	def version_range(self):
		return copy.deepcopy(self.__version)
		
## Object that stores OS information for the current system
class os_info(object):
	
	## Creates a os_info object
	#
	# Automatically populates data on current system
	#
	def __init__(self):
		self.__os_type = None
		self.__os_flavor = None
		self.__os_version = (None, None)

		self.__fill()
		
	def __fill(self):
		raw_type = platform.system()
		if raw_type == "Linux":
			self.__os_type = validate_os('linux')
		elif raw_type == "Windows":
			#self.__os_type = OS.WINDOWS
			self.__os_type = None
		else:
			self.__os_type = None

		if self.__os_type == None:
			return
			
		if self.__os_type == validate_os('linux'):
			
			my_dist = platform.linux_distribution()
			
			if 'ubuntu' in my_dist[0].lower():
				self.__os_flavor = validate_flavor('linux', 'ubuntu')
				#print("!:" + self.__os_flavor)
			elif 'centos' in my_dist[0].lower():
				self.__os_flavor = validate_flavor('linux', 'centos')
			else:
				self.__os_flavor = None

			if not self.__os_flavor == None:
				self.__os_version = version_util.version(my_dist[1])
	
	## Retrieves the gathered OS flavor
	#
	# @returns string - The gathered OS flavor 
	#
	def flavor(self):
		return copy.deepcopy(self.__os_flavor)
	
	## Retrieves the gathered OS flavor 
	#
	# @returns string - The gathered OS flavor 
	#	
	def os_type(self):
		return copy.deepcopy(self.__os_type)
	
	## Retrieves the gathered OS version 
	#
	# @returns string - The gathered OS version 
	#
	def version(self):
		return copy.deepcopy(self.__os_version)

	## Compares the data gathered to the provided os_match object
	#
	# @param os_match match_obj - The match object to compare the current system to
	# @returns True if system matches, False if not
	#
	def matches(self, match_obj):
		
		# Auto-fail if our system is unsupported
		if self.__os_type == None:
			return False
		
		if not isinstance(match_obj, os_match):
			raise ValueError("Object is not a os_match object")
		else:
			# Test the OS type
			if not match_obj.os_type() == self.__os_type:
				return False
				
			if match_obj.flavor() == "-":
				return False
			elif match_obj.flavor() == "*":
				pass
			elif not match_obj.flavor() == self.__os_flavor:
				return False
				
			if match_obj.version_range() == "*":
				return True
			elif match_obj.version_range().in_range(self.__os_version):
				return True
			else:
				return False




