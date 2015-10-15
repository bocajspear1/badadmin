## This module provides easy access to basic OS type information
#

import sys
import platform
import copy
from util.cross_version import Enum
import util.version_string as version_string 

__os_list = {
	'LINUX': [
		#'DEBIAN',
		'CENTOS', 
		#'SUSE',
		'UBUNTU', 
		'UNSUPPORTED' 
	],
	'WINDOWS': [
		'WIN_7',
		'WIN_8',
		'WIN_8_1',
		'WIN_SERVER_2003', 
		'WIN_SERVER_2008',
		'WIN_SERVER_2012',
		'WIN_XP',
		'WIN_9x', 
		#'REACTOS',
		'UNSUPPORTED'
	]
	
}



    
OS = Enum(['LINUX', 'WINDOWS'])
LINUX = Enum(['CENTOS', 'UBUNTU'])  


class os_match(object):
	
	def __init__(self, os_type, flavor='*', version_range='*'):
		
		if type(os_type) == OS:
			self.__os_type = os_type
		else:
			raise ValueError("Invalid OS type")
			
		
		if flavor == '*' or flavor == "-":
			self.__flavor = flavor
		elif self.__os_type == OS.WINDOWS and type(flavor) == WINDOWS:
			self.__flavor = flavor
		elif self.__os_type == OS.LINUX and type(flavor) == LINUX:
			self.__flavor = flavor
		else:
			raise ValueError("Invalid OS flavor")
			
			
		if version_string.is_range(version_range):
			self.__version_range = version_range
		else:
			raise ValueError("Invalid OS version range")
		
	def flavor(self):
		return copy.deepcopy(self.__os_flavor)
		
	def os_type(self):
		return copy.deepcopy(self.__os_type)

	def version_range(self):
		return copy.deepcopy(self.__os_version)
		

class os_info(object):
	
	def __init__(self):
		self.__os_type = None
		self.__os_flavor = None
		self.__os_version = (None, None)

		self.__fill()
		
	def __fill(self):
		raw_type = platform.system()
		if raw_type == "Linux":
			self.__os_type = OS.LINUX
		elif raw_type == "Windows":
			#self.__os_type = OS.WINDOWS
			self.__os_type = OS.UNSUPPORTED
		else:
			self.__os_type = OS.UNSUPPORTED

		if self.__os_type == OS.UNSUPPORTED:
			return
			
		if self.__os_type == OS.LINUX:
			my_dist = platform.linux_distribution()
			
			if 'ubuntu' in my_dist[0].lower():
				self.__os_flavor = LINUX.UBUNTU
				#print("!:" + self.__os_flavor)
			elif 'centos' in my_dist[0].lower():
				self.__os_flavor = LINUX.CENTOS
			else:
				self.__os_flavor = LINUX.UNSUPPORTED

			if not self.__os_flavor == LINUX.UNSUPPORTED:
				self.__os_version = my_dist[1]

	def flavor(self):
		
		return copy.deepcopy(self.__os_flavor)
		
	def os_type(self):
		return copy.deepcopy(self.__os_type)

	def version(self):
		return copy.deepcopy(self.__os_version)

	# Returns true if the match_obj matches our system, False if not
	def check_match(self, match_obj):
		
		# Auto-fail if our system is unsupported
		if self__os_type == OS.UNSUPPORTED:
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
			elif version_string.test_range(match_obj.version_range(), self.__os_version):
				return True
			else:
				return False




