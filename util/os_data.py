## This module provides easy access to basic OS type information
#

import sys
import platform
import copy
from util.cross_version import Enum
import util.version_util as version_util


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
		'win_XP',
		'WIN_9x', 
		#'REACTOS',
	]
	
}

def valid_os(os_type):
	if os_type in _os_list:
		return True
	else:
		return False
		
def valid_flavor(os_type, flavor):
	if not valid_os(os_type):
		return False
	
	if flavor in _os_list[os_type]:
		return True
		
	return False

# Inline functions used to make sure I don't misspell anything :)
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

## Object that represents a os match and is used in comparing the current OS, stored in 'os_info' to
# a desired os, which is stored in 'os_match'
class os_match(object):
	
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
		
	def flavor(self):
		return copy.deepcopy(self.__flavor)
		
	def os_type(self):
		return copy.deepcopy(self.__os_type)

	def version_range(self):
		return copy.deepcopy(self.__version)
		
## Object that stores OS information for the current system
class os_info(object):
	
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

	def flavor(self):
		return copy.deepcopy(self.__os_flavor)
		
	def os_type(self):
		return copy.deepcopy(self.__os_type)

	def version(self):
		return copy.deepcopy(self.__os_version)

	# Returns true if the match_obj matches our system, False if not
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




