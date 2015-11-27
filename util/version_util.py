import util.cross_version as cross_version
import copy
import re

class version(object):
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
	
		
	def major(self):
		return self.__v_tuple[0]
		
	def minor(self):
		return self.__v_tuple[1]
		
	def get_tuple(self):
		return copy.deepcopy(self.__v_tuple)
	
	def __normalize(self, other_tuple):
		
		other_len = len(other_tuple)
		my_len = len(self.__v_tuple)
		
		if my_len > other_len:
			diff = my_len - other_len
			other_tuple += (0,) * diff
			
		elif other_len > my_len:
			diff = other_len - my_len 
			self.__v_tuple += (0,) * diff
		
		return other_tuple
		
	def __lt__(self, other):
		if not isinstance(other, version):
			other = version(other)
		
		other_tuple = self.__normalize(other.get_tuple())
		return self.__v_tuple < other_tuple
	
	def __le__(self, other):
		if not isinstance(other, version):
			other = version(other)
		other_tuple = self.__normalize(other.get_tuple())
		return self.__v_tuple <= other_tuple
		
	def __gt__(self, other):
		if not isinstance(other, version):
			other = version(other)
		other_tuple = self.__normalize(other.get_tuple())
		return self.__v_tuple > other_tuple
	
	def __ge__(self, other):
		if not isinstance(other, version):
			other = version(other)
		other_tuple = self.__normalize(other.get_tuple())
		return self.__v_tuple >= other_tuple
	
	def __eq__(self, other):
		if other == None:
			return False
			
		if not isinstance(other, version):
			other = version(other)
		other_tuple = self.__normalize(other.get_tuple())
		return self.__v_tuple == other_tuple
		
	def __ne__(self, other):
		if not isinstance(other, version):
			other = version(other)
		other_tuple = self.__normalize(other.get_tuple())
		return self.__v_tuple != other_tuple

class version_range(object):
	
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
			raise ValueError("Invalid range")	
	
	def get_string(self):
		return self.__string
			
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
	
	def extract_version(self):
		return copy.deepcopy(self.__version)
	
	def extract_direction(self):
		return self.__range_direction
	
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
	
	def __eq__(self, other):
		
		if other == None:
			return False
		
		if not isinstance(other, version_range):
			other = version_range(other)

		
		return other.extract_direction() == self.extract_direction() and other.extract_version() == self.extract_version()
		
def is_range(value):
	if not cross_version.isstring(value):
		return False
	
	if value == "*" or value == "-":
		return True
	
	if not (value.startswith(">") or value.startswith("<") or value.startswith("=")) or len(value) < 2:
		return False
	
	
	return True


#~ ## Compares the given input string to the current vulnerability's
#~ # version. Returns a number (1-, 0, 1) based on the relation of the input
#~ # version to the internal version. Does not take versions with >/</= in
#~ # front of them, will throw an error
#~ #
#~ # -1 = The inputted version is lower then the internal version
#~ # 0 = The inputted version is equal to the internal version
#~ # 1 = the inputted version is greater the than the internal version
#~ # 
#~ # @param {string} version - The version to compare
#~ # @returns {integer}
#~ #	
#~ def compare_version(test_version, comparison_version):
	
	#~ if not cross_version.isstring(test_version) or not cross_version.isstring(comparison_version):
		#~ raise ValueError("Versions must be strings")
	
	#~ if not test_version.startswith(">") and not test_version.startswith("<") and not test_version.startswith("="):
		#~ if test_version > comparison_version:
			#~ return 1
		#~ elif test_version == comparison_version:
			#~ return 0
		#~ elif test_version < comparison_version:
			#~ return -1
		#~ else:
			#~ raise ValueError("Range found where version expected")	
		
	#~ else:
		#~ raise ValueError("Invalid version")	
	
#~ ## Tests vulnerability version against a given version to see if the vulnerability
#~ # version falls within the bounds of the inputted version
#~ #
#~ # @param {string} version_range - The version string to test the vulnerability against
#~ # @returns {boolean} = True if the vulnerabilty version passes, False if it does not
#~ #
#~ def test_range(version_range, test_version):
	
	#~ if not cross_version.isstring(version_range):
		#~ raise ValueError("Invalid version comparison")	
	
	#~ range_data = range_extract(version_range)
	
	#~ if range_data[0] == "<=":
		#~ if test_version <= range_data[1]:
			#~ return True
		#~ else:
			#~ return False
	#~ elif range_data[0] == ">=":
		#~ if test_version >= range_data[1]:
			#~ return True
		#~ else:
			#~ return False
	#~ elif range_data[0] == "<":
		#~ if test_version < range_data[1]:
			#~ return True
		#~ else:
			#~ return False
	#~ elif range_data[0] == ">":
		#~ if test_version > range_data[1]:
			#~ return True
		#~ else:
			#~ return False
	#~ elif range_data[0] == "=":
		#~ if test_version == range_data[1]:
			#~ return True
		#~ else:
			#~ return False
	#~ else:
		#~ raise ValueError("Invalid range")


#~ def range_extract(version_range):
	
	#~ if not cross_version.isstring(version_range):
		#~ raise ValueError("Invalid value for range_extract")	
	
	#~ range_dir = ""
	#~ only_version = ""
	
	#~ if version_range.startswith("<=") or version_range.startswith(">="):
		#~ range_dir = version_range[:2]
		#~ only_version = version_range[2:]
	#~ elif version_range.startswith("<") or version_range.startswith(">") or version_range.startswith("="):
		#~ range_dir = version_range[:1]
		#~ only_version = version_range[1:]
	#~ else:
		#~ range_dir = "="
		#~ only_version = version_range
		
	#~ return (range_dir, only_version)

#~ # Rules:
#~ # Return True if ranges intersect
#~ # Return False ranges do not intersect
#~ def ranges_intersect(range1, range2):
	
	#~ range1_data = range_extract(range1)
	#~ range2_data = range_extract(range2)
	
	#~ HAS_EQUAL = [">=", "<=", "="]
	
	#~ if ((range1_data[0] == "<" or range1_data[0] == "<=") and 
		#~ range1_data[1] < range2_data[1] and 
		#~ (range2_data[0] == ">" or range2_data[0] == ">=") ):
		#~ return False
	#~ elif ((range2_data[0] == "<" or range2_data[0] == "<=") and 
		#~ range2_data[1] < range1_data[1] and 
		#~ (range1_data[0] == ">" or range1_data[0] == ">=")  ):
		#~ return False
	#~ elif (range1_data[1] == range2_data[1] and (range1_data[0] not in HAS_EQUAL or range2_data[0] not in HAS_EQUAL)):
		#~ return False
	#~ else:
		#~ return True
