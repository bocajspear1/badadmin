import os
import random
import util.cross_version as cross_version
import util.version_util as version_util
import copy
import sys
#import subprocess
from util.simple_filesystem import simple_file
from util.simple_filesystem import simple_dir
from util.simple_command import simple_command
from util.simple_packages import simple_packages
from util.ba_random import ba_random as random_class
import util.os_data as os_data
import base64


#PYTHON_VERSION = sys.version_info.major

def init():
	util_path = "./util"
	if not util_path in sys.path:
		sys.path.append(util_path) 

def convert_difficulty(difficulty):
	if difficulty == "easy":
		return 1
	elif difficulty == "medium":
		return 2
	elif difficulty == "hard":
		return 3
	else:
		raise ValueError("Invalid string for difficulty")
		
## Base class for dependency related classes (links and restrictions)
class dependency_base(object):
	def __init__(self, provides_string, version_range):
		
		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string is not a string")
		else:
			self.__provides_string = provides_string
	
		self.__version_range = version_util.version_range(version_range)
	
	
	def provides_string(self):
		return copy.deepcopy(self.__provides_string)
		
	def version_range(self):
		return copy.deepcopy(self.__version_range)
		
## Represents a link between a vulnerability and possible vulnerailities
# that provide the requested service or application
#
#
class dependency_link(dependency_base):
	pass
	
## Represents a restriction on the current modules vulnerabilities based on the
# version of an application they provide
class version_restriction(dependency_base):
	

	# Check if the provides string and version do not fall under the restriction
	def version_pass(self, provides_string, version_string):
		
		if not self.provides_string() == provides_string:
			return False
			
		if version_string == None:
			return True
		
		if isinstance(version_string, version_util.version):
			version_obj = version_string
		elif cross_version.isstring(provides_string):
			print(version_string)
			version_obj = version_util.version(version_string)
		else:
			raise ValueError("Provides string is not a string or version object")

		
		
		if not self.version_range().in_range(version_obj):
			return False
			
		return True

## Represents a restriction on the versions a vulnerabilities depends can provide. 
# This will become the dependencies version restrictions
class dependency_restriction(dependency_base):
	def range_pass(self, provides_string, version_range):
		
		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string is not a string")
		
		range_obj = version_util.version_range(version_range)
		
		if not self.__provides_string == provides_string:
			return False
		
		if not range_obj.intersects(self.__version_range):
			return False
			
		return True

## Represents a single vulnerability
#
# A module will have at least one vulnerability, the special NONE vulnerability
# which indicates that no vulneraility is installed
#	
class vulnerability(object):
	
	## Constructor
	#
	# @param {string} name - The name of the vulnerability
	# @param {string} description - A short description of what the vulnerability does
	# @param {string} provides - What this vulnerability will provide (defaults to blank)
	# @param {string} provides_version - The version number of the item installed by the vulnerability
	#
	def __init__(self, name, description, provides='', provides_version=''):
		if (not cross_version.isstring(name) or not cross_version.isstring(description) 
			or not cross_version.isstring(provides) or not cross_version.isstring(provides_version)):
			raise ValueError("All values must be strings")
		
		self.__name = name
		self.__description = description
		if provides.strip() == "":
			self.__provides = None
		else:
			self.__provides = provides
		if provides_version.strip() == '':
			self.__version = None
		else:
			self.__version = version_util.version(provides_version)
		self.__dependencies = []
		self.__cmd_uses = []
		self.__cmd_modifies = []
		self.__supported_os_list = []
		self.__difficulty = None

	## Returns the name of the vulnerability
	# 
	# @returns {string}
	#
	def get_name(self):
		return self.__name

	## Returns the description of the vulnerability
	# 
	# @returns {string}
	#
	def get_description(self):
		return self.__description
	
	## Returns what the vulnerability provides
	# 
	# @returns {string}
	#
	def get_provides(self):
		return self.__provides
	
	## Returns the version of what the vulnerabilty provides
	# 
	# @returns {string} - The version
	#
	def get_version(self):
		return copy.deepcopy(self.__version)
	
	## Compares the given input string to the current vulnerability's
	# version. Returns a number (1-, 0, 1) based on the relation of the input
	# version to the internal version. Does not take versions with >/</= in
	# front of them, will throw an error
	#
	# -1 = The inputted version is lower then the internal version
	# 0 = The inputted version is equal to the internal version
	# 1 = the inputted version is greater the than the internal version
	# 
	# @param {string} version - The version to compare
	# @returns {integer}
	#	
	#~ def compare_version(self, version):
		#~ return version_utilversion_string.compare_version(version, self.__version)
	
	## Tests vulnerability version against a given version to see if the vulnerability
	# version falls within the bounds of the inputted version
	#
	# @param {string} required_range - The version string to test the vulnerability against
	# @returns {boolean} = True if the vulnerabilty version passes, False if it does not
	#
	def is_in_range(self, required_range):
		
		if self.__version == None:
			return False
		
		if not isinstance(required_range, version_util.version_range):
			required_range = version_util.version_range(required_range)
		
		return required_range.in_range(self.__version)
	
	## Adds a dependency and its version range
	# 
	# @param {string} provides_value - The version string to test the vulnerability 
	# @param {string} version_range - The required version range of the dependency
	#	
	def add_dependency(self, provides_value, version_range):
		if not cross_version.isstring(provides_value) or not cross_version.isstring(version_range):
			raise ValueError("All values must be strings")
		else:
			dep_item = dependency_link(provides_value, version_range)
			self.__dependencies.append(dep_item)
	
	## Returns a list of dependencies
	# 
	# @returns {string[]} = List of dependencies
	#	
	def get_dependencies(self):
		return copy.deepcopy(self.__dependencies)
	
	## Adds a link to the vulnerability. Usually a link to a page describing what the vulneraility
	# does.
	# 
	# @param {string} link - The link to add
	#		
	def set_link(self, link):
		if cross_version.isstring(link) and link.startswith("http://") or link.startswith("https://"):
			self.__link = link
		else:
			raise ValueError("Invalid link")	
	
	## Returns the vulnerability link
	# 
	# @returns {string} = The link
	#
	def get_link(self):
		return self.__link
		
	## Adds a command that the vulnerability uses to a list
	# 
	# @param {string} link - The command to add
	#
	def add_cmd_uses(self, cmd):
		if cross_version.isstring(cmd): 
			if not cmd in self.__cmd_uses:
				self.__cmd_uses.append(cmd)
		else:
			raise ValueError("Invalid command")	
	
	## Adds a command that the vulnerability modifies to a list
	# 
	# @param {string} link - The command to add
	#	
	def add_cmd_modifies(self, cmd):
		if cross_version.isstring(cmd):
			if not cmd in self.__cmd_modifies:
				self.__cmd_modifies.append(cmd)
		else:
			raise ValueError("Invalid command")	
	
	## Returns a list of commands the vulnerability uses
	# 
	# @returns {string[]} 
	#
	def get_cmd_uses(self):
		return copy.deepcopy(self.__cmd_uses)
		
	## Returns a list of commands the vulnerability modifies
	# 
	# @returns {string[]}
	#	
	def get_cmd_modifies(self):
		return copy.deepcopy(self.__cmd_modifies)

	
	def add_supported_os(self, os_type, flavor="*", version="*"):
		insert_os = os_data.os_match(os_type, flavor, version)
		self.__supported_os_list.append(insert_os)
		
	def check_os_support(self):
		system_info = os_data.os_info()
		if len(self.__supported_os_list) == 0:
			return True
			
		for supported_os in self.__supported_os_list:
			if system_info.matches(supported_os):
				return True
		return False
	
	# Higher is more difficult
	def set_difficulty(self, difficulty):
		if cross_version.isinteger(difficulty):
			if difficulty >= 1 and difficulty <= 3:
				self.__difficulty = difficulty
			else:
				raise ValueError("Invalid difficulty number ( Must be 1 - 3 )")
				return
		elif cross_version.isstring(difficulty):
			self.__difficulty = convert_difficulty(difficulty)
		else:
			raise ValueError("Invalid type for difficulty")	
	
	def get_difficulty(self):
		return self.__difficulty
		
class doc():
	
	def __init__(self):
		self.__doc_list = []
	
	def add_doc(self, module, vuln, description):
		
		if not cross_version.isstring(module):
			raise ValueError("Module value is not a string")
		
		if not cross_version.isstring(vuln):
			raise ValueError("Vulnerabilty value is not a string")
			
		if not cross_version.isstring(description):
			raise ValueError("Description value is not a string")
			
		self.__doc_list.append({"module": module, "vulnerability": vuln, "description": description})

	def encrypt_doc(self, key):
		pass
		
	def base64_doc(self):
		doc_string = self.__doc_to_string()
		
		if doc_string.strip() == "":
			return ""
		else:
			output = base64.standard_b64encode(doc_string)
			return output
		
	def __doc_to_string(self):
		
		out_string = ""
		
		for doc_item in self.__doc_list:
			out_string += "Module: " + doc_item['module']
			out_string += " [" + doc_item['vulnerability']
			out_string += "] - " + doc_item['description'] + "\n"
		
		return out_string
	


## This class is the base class for BadAdmin modules
# It provides a number of useful functions for easy module creation
#
class module_base(object):
	
	def __init__(self):
		self.__vulnerability_list = {}
		self.__multi_vuln = False
		self.__running_vulns = []
		
		self.__version_restrictions = []
		self.__dependency_restrictions = []
		self.__commands_modified_restrictions = []
		
		self.__tmp_version_restrictions = []
		self.__tmp_dependency_restrictions = []
		
		self.doc = doc()
		self.__difficulty = None
# Start abstract functions
	# Can't use Python abc functionality due to Python2/3 compatability
	
	## ABSTRACT: Returns the name of the module
	def name(self):
		raise NotImplementedError 
	
	## ABSTRACT: Returnes the version of the module. NOT related to any version of application the module installs
	def version(self):
		raise NotImplementedError 
	
	## ABSTRACT: Returns the author of the module
	def author(self):
		raise NotImplementedError 
	
	## ABSTRACT: Returns a description of the module
	def description(self):
		raise NotImplementedError 
		
	## ABSTRACT: Function for when the vulnerabilities are run
	def run(self, options={}):
		raise NotImplementedError 
	
	## This function is called with a vulnerabilty object and values in the options for testing the functionality of module
	def test_run(self, vuln_obj, options={}):
		raise NotImplementedError 
	
# End abstract functions

	## Function for producing a blurb about the module
	def info(self):
		show_string = "\nName: " + self.name() + "\n\n"
		show_string += "Version: " + self.version() + "\n"
		show_string += "Author: " + self.author() + "\n\n"
		show_string += "Description:\n" + self.description() + "\n\n"
		return show_string


	## Allows access to create a new vulnerability object
	#
	def _new_vulnerability(self, name, description, provides='', provides_version=''):
		return vulnerability(name, description, provides, provides_version)
		
	def _add_vulnerability(self, vulnerability_obj):

		if isinstance(vulnerability_obj, vulnerability):
			self.__vulnerability_list[vulnerability_obj.get_name()] = vulnerability_obj
		else:
			raise ValueError("Object is not an instance of vulnerability")
	
	## Clears all vulnerabilities in the modules. Use only for testing 
	def _clear_vulnerabilities(self):
		self.__vulnerability_list = []
	
	## Return a vulnerability object by name. Used in module testing
	def get_vulnerability_object(self, vuln_name):
		
		if not cross_version.isstring(vuln_name):
			raise ValueError("Name is not string")
		
		if vuln_name in self.__vulnerability_list:
			return self.__vulnerability_list[vuln_name]
		else:
			return False
	
	def set_multi_vuln(self, value):
		if value == True or value == False:
			self.__multi_vuln = value
		else:
			raise ValueError("Invalid multi_vuln value")

# Functions for dependency resolution
	def has_provides(self, search):
		for vuln in self.__vulnerability_list:
			if self.__vulnerability_list[vuln].get_provides() == search:
				return True
		
		return False

	def has_difficulty(self, search):
		
		if cross_version.isstring(search):
			search = convert_difficulty(search)
		
		if not cross_version.isinteger(search):
			raise ValueError("Invalid difficulty")
		
		for vuln in self.__vulnerability_list:
			if self.__vulnerability_list[vuln].get_difficulty() == search or self.__vulnerability_list[vuln].get_difficulty() == None:
				return True
		
		return False

	## Generates a list of vulnerabilities that fit within current restrictions
	def __restricted_list(self):
		
		if len(self.__vulnerability_list) == 0:
			return []
		
		valid_list = []
		
		for vuln_name in self.__vulnerability_list:
			vuln = self.__vulnerability_list[vuln_name]
			valid = True
			
			
			# Restrict by difficulty
			if not self.__difficulty == None:
				if not vuln.get_difficulty() <= self.__difficulty:
					valid = False
			
			# Restrict by version restrictions
			for ver_restrict in self.__version_restrictions:
				if not ver_restrict.version_pass(vuln.get_provides(), vuln.get_version()):
					valid = False
			
			# Restrict by dependency restrictions
			for dep_restrict in self.__dependency_restrictions:
				for dep in vuln.get_dependencies():
					if dep_restrict.provides_string() == dep.provides_string():
						if not dep_restrict.range_pass(dep.provides_string(), dep.version_range()):
							valid = False
			
			
			# Restrict by version restrictions (Temporary entries)
			for ver_restrict in self.__tmp_version_restrictions:
				if not ver_restrict.version_pass(vuln.get_provides(), vuln.get_version()):
					valid = False
			
			# Restrict by dependency restrictions (Temporary entries)
			for dep_restrict in self.__tmp_dependency_restrictions:
				for dep in vuln.get_dependencies():
					if dep_restrict.provides_string() == dep.provides_string():
						if not dep_restrict.range_pass(dep.provides_string(), dep.version_range()):
							valid = False
			
			if vuln.check_os_support() == False:
				valid = False
			
			if valid == True:
				valid_list.append(vuln)
				
		return copy.deepcopy(valid_list)
		
	## Generates a list of vulnerabilities that the module has selected for running based on current restrictions
	def generate_vulnerabilities(self):
		valid_vulns = self.__restricted_list()
			
		rand_gen = self.random()
		
		return_list = []
		
		if len(valid_vulns) == 0:
			return []
		elif not self.__multi_vuln:
			vuln = rand_gen.array_random(valid_vulns)
			return_list.append(copy.deepcopy(vuln))
		else:
			for vuln in valid_vulns:
				if rand_gen.will_do():
					return_list.append(copy.deepcopy(vuln))
	
		return return_list
	
	def get_vulnerabilities(self):
		
		if len(self.__running_vulns) == 0:
			self.__running_vulns = self.generate_vulnerabilities()
			
		return copy.deepcopy(self.__running_vulns)
	
	def set_difficulty_limit(self, limit):
		if not cross_version.isinteger(limit):
			raise ValueError("Difficulty limit must be integer format")
		
		if limit == 0:
			self.__difficulty = None
		else:
			self.__difficulty = limit 
	
		
	def add_temp_version_restrictions(self, provides_string, version_range):
		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string must be a string")
			
		for restriction_item in self.__version_restrictions:
			if restriction_item.version_range() == version_range and restriction_item.provides_string() == provides_string:
				return
		
		self.__tmp_version_restrictions.append( version_restriction(provides_string, version_range) )
	
	
	## Restrict the use of certain dependencies temporarily (used in dependency resolution)
	def add_temp_dependency_restriction(self, provides_string, version_range):
		
		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string must be a string")
			
		
		for restriction_item in self.__dependency_restrictions:
			if restriction_item.version_range() == version_range and restriction_item.provides_string() == provides_string:
				return
		
		self.__tmp_dependency_restrictions.append( restriction(provides_string, version_range) )
		
	## Restrict what version range can be returned	
	def add_version_restriction(self, provides_string, version_range):
		
		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string must be a string")
			
		for restriction_item in self.__version_restrictions:
			if restriction_item.version_range() == version_range and restriction_item.provides_string() == provides_string:
				return
		
		self.__version_restrictions.append( version_restriction(provides_string, version_range) )
		
	## Restrict the use of certain dependencies
	def add_dependency_restriction(self, provides_string, version_range):
		
		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string must be a string")
			
		
		for restriction_item in self.__dependency_restrictions:
			if restriction_item.version_range() == version_range and restriction_item.provides_string() == provides_string:
				return

		#~ self.__version_restrictions = {}
		#~ self.__dependency_restrictions = {}
		#~ self.__commands_modified_restrictions = []

		
		self.__dependency_restrictions.append( restriction(provides_string, version_range) )
	
	def get_dependency_restrictions(self):
		return copy.deepcopy(self.__dependency_restrictions)
	
	def add_command_used_restrictions(self, command_used):
		self.commands_used_restrictions.append(command_used)
	
	def add_command_modified_restrictions(self, command_modified):
		self.commands_modified_restrictions.append(command_modified)

	def get_class_name(self):
		return self.__class__.__name__

# Methods for returning useful functionality to modules
	def os_matches(self, type_string, flavor_string="*", version_string="*"):
		matcher = os_data.os_match(type_string, flavor_string, version_string)
		return self.os_info().matches(matcher)

	def os_info(self):
		return os_data.os_info()

	def random(self):
		return random_class()
		
	def file(self, filename):
		return simple_file(filename)
		
	def dir(self, dirname):
		return simple_dir(dirname)	

	def command(self):
		return simple_command()

	def cross_version(self):
		return cross_version

	def package_manager(self):
		return simple_packages()
