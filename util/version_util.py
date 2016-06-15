## @package util.version_util
#
# Simplified manipulation of versions and version ranges.
#
# A version is defined as n.nx[[.nx].nx], where n is one or more numbers, and x is one or more characters. It can have 2 to 4 . seperated sections. 
# Single integers have '.0' appended to them
#
import util.cross_version as cross_version
import copy
import re

## @class version
#
# Represents a version of an application.
# 
# Versions are comparable (e.g. ==, <) to other version objects
# 
#
class version(object):
	
	## Create a version object
	#
	# @param input_string (string) - Version in string format
	def __init__(self, input_string):
		
		if not cross_version.isstring(input_string):
			raise ValueError("Version must be a string")
		
		version_list = input_string.split(".")
		
		if len(version_list) == 1 and str(version_list[0]).isdigit():
			version_list.append('0')
		elif len(version_list) < 2:
			raise ValueError("Invalid version string")
		elif len(version_list) > 4:
			raise ValueError("Invalid version string")
			
		final_version_list = []
		
		for i in range(len(version_list)):
			current = version_list[i]
			if i == 0 and not current.isdigit():
				raise ValueError("Invalid version string. First section must be an integer")
			else:
				if current.isdigit():
					final_version_list.append(int(current))
					if i > 0:
						final_version_list.append('')
				else:
					# Check for numbers followed by 
					check = re.match(r"^([0-9]+)([a-zA-Z]+).*$", current)
					if not check == None:
						check_groups = check.groups()
						final_version_list.append(int(check_groups[0]))
						final_version_list.append(check_groups[1])
					else:
						pass

		if len(final_version_list) < 3 or len(final_version_list) > 7:
			raise ValueError("Invalid version string")
			
		self.__v_tuple = tuple(final_version_list)
	
	## Returns the major version number	(Major.Minor.Other)
	#
	# @returns int - The major version number
	def major(self):
		return self.__v_tuple[0]
	
	## Returns the minor version number	(Major.Minor.Other)
	#
	# @returns int - The minor version number	
	def minor(self):
		return self.__v_tuple[1]
	
	## Returns a copy of the tuple that stores the version information
	#
	# @returns int - The minor version number	
	def get_tuple(self):
		return copy.deepcopy(self.__v_tuple)
	
	# Ensures during a comparison, the tuples are of the same size
	def __normalize(self, other_tuple):
		
		other_len = len(other_tuple)
		my_len = len(self.__v_tuple)

		if my_len > other_len:
			diff = int((my_len - other_len) / 2)
			other_tuple += (0, '') * diff
		
		elif other_len > my_len:
			diff = int((other_len - my_len) / 2)
			self.__v_tuple += (0, '') * diff
		
		return other_tuple

## @cond HIDDEN
	
	## Less than (<) comaprison	
	def __lt__(self, other):
		if not isinstance(other, version):
			other = version(other)

		other_tuple = self.__normalize(other.get_tuple())
		return self.__v_tuple < other_tuple
		
	## Less than or equal to (<=) comaprison	
	def __le__(self, other):
		if not isinstance(other, version):
			other = version(other)
		other_tuple = self.__normalize(other.get_tuple())
		return self.__v_tuple <= other_tuple
	
	## Greater than (>) comaprison	
	def __gt__(self, other):
		if not isinstance(other, version):
			other = version(other)
		other_tuple = self.__normalize(other.get_tuple())
		return self.__v_tuple > other_tuple
	
	## Greater than or equal to (>=) comaprison	
	def __ge__(self, other):
		if not isinstance(other, version):
			other = version(other)
		other_tuple = self.__normalize(other.get_tuple())
		
		return self.__v_tuple >= other_tuple
		
	## Equal to (==) comaprison	
	def __eq__(self, other):
		if other == None:
			return False
			
		if not isinstance(other, version):
			other = version(other)
		other_tuple = self.__normalize(other.get_tuple())
		return self.__v_tuple == other_tuple
	
	## Not equal to (!=) comaprison	
	def __ne__(self, other):
		if not isinstance(other, version):
			other = version(other)
		other_tuple = self.__normalize(other.get_tuple())
		return self.__v_tuple != other_tuple

## @endcond

## @class version_range
#
# Represents a version range
#
# Can be compared for equality to other version_range objects
#
class version_range(object):
	
	## Create a version object
	#
	# @param version_range_string (string) - Version range in string format
	def __init__(self, version_range_string):
		if not cross_version.isstring(version_range_string):
			raise ValueError("Invalid value for range")	
	
		self.__range_direction = ""
		self.__version = None
		self.__string = version_range_string
		
		
		
		if version_range_string == "*" or version_range_string == "-":
			self.__range_direction = version_range_string
			self.__version = None
		elif version_range_string.startswith("<=") or version_range_string.startswith(">="):
			self.__range_direction = version_range_string[:2]
			self.__version = version(version_range_string[2:])
		elif version_range_string.startswith("<") or version_range_string.startswith(">") or version_range_string.startswith("="):
			self.__range_direction = version_range_string[:1]
			self.__version = version(version_range_string[1:])
		else:
			raise ValueError("Invalid range: " + version_range_string)	
	
	## Get the original string
	#
	# @returns string - Original string
	#
	def get_string(self):
		return self.__string
	
	
	## Compares a version object to the range to see if the value in the
	# version object falls within the range
	# 
	# @param check (version) - Version object to check 
	#
	# @returns bool
	#
	def in_range(self, check):
		if not isinstance(check, version):
			check = version(check)
		
		if self.__range_direction == "*":
			return True
		elif self.__range_direction == "-":
			return False
		elif self.__range_direction == ">":
			return check > self.__version
		elif self.__range_direction == ">=":
			return check >= self.__version
		elif self.__range_direction == "<":
			return check < self.__version
		elif self.__range_direction == "<=":
			return check <= self.__version
		elif self.__range_direction == "=":
			return check == self.__version
		else:
			raise ValueError("Invalid direction")
	
	## Returns just the version stored in the range
	# 
	# @returns version - Version object
	#
	def extract_version(self):
		return copy.deepcopy(self.__version)
	
	## Returns just the direction(<,>,==, etc.) stored in the range
	# 
	# @returns string - Direction in string format
	#
	def extract_direction(self):
		return self.__range_direction
	
	## Compares another version range to the current range to see if they
	# will at any point intersect
	#
	# @param other (version_range) - Version range object to check 
	#
	# @returns bool
	#
	def intersects(self, other):
		other_version = other.extract_version()
		
		if other_version == self.__version:
			if other.in_range(self.__version) and self.in_range(other_version):
				return True
			else:
				return False
		elif other.in_range(self.__version) or self.in_range(other_version):
			return True
		else:
			return False
## @cond HIDDEN

	def __eq__(self, other):
		
		if other == None:
			return False
		
		if not isinstance(other, version_range):
			other = version_range(other)

		
		return other.extract_direction() == self.extract_direction() and other.extract_version() == self.extract_version()
	
	def __str__(self):
		return "RANGE: " + self.__string 
	
## @endcond
		

