## @package modules.base
#
# Provides basic classes for BadAdmin modules
#
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
from util.network import networking
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
	
	## Create a new dependency base object. Don't directly create one of these.
	#
	def __init__(self, provides_string, version_range):
		
		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string is not a string")
		else:
			self.__provides_string = provides_string
	
		self.__version_range = version_util.version_range(version_range)
	
	## The provides string of the link or dependency
	#
	# @returns string - The provides string
	#
	def provides_string(self):
		return copy.deepcopy(self.__provides_string)
	
	## The version_range object of the item
	#
	# @returns version_range - The version_range
	#	
	def version_range(self):
		return copy.deepcopy(self.__version_range)
		
## Represents a link between a vulnerability and possible modules that provide the required 
# provides string
#
class dependency_link(dependency_base):
	pass
	
## Represents a restriction on the current modules vulnerabilities based on the
# version of an application they provide
class version_restriction(dependency_base):
	

	## Check if the provides string and version do not fall under the restriction
	def version_pass(self, provides_string, version_string):
		
		if not self.provides_string() == provides_string:
			return False
			
		if version_string == None:
			return True
		
		if isinstance(version_string, version_util.version):
			version_obj = version_string
		elif cross_version.isstring(provides_string):
			version_obj = version_util.version(version_string)
		else:
			raise ValueError("Provides string is not a string or version object")

		if self.version_range().in_range(version_obj):
			return True
			
		return False

## Represents a restriction on the versions a vulnerabilities depends can provide. 
# This will become the dependencies version restrictions
class dependency_restriction(dependency_base):
	def range_pass(self, provides_string, version_range):
		
		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string is not a string")
		
		if not isinstance(version_range, version_util.version_range):
			range_obj = version_util.version_range(version_range)
		else:
			range_obj = version_range
		
		if not self.provides_string() == provides_string:
			return False
		
		if range_obj.intersects(self.version_range()):
			return True
			
		return False

## Represents a single vulnerability
#
# A module will have at least one vulnerability, the special NONE vulnerability
# which indicates that no vulneraility is installed
#	
class vulnerability(object):
	
	## Constructor
	#
	# @param name (string) - The name of the vulnerability
	# @param description (string) - A short description of what the vulnerability does
	# @param provides (string) - What this vulnerability will provide (defaults to blank)
	# @param provides_version (string) - The version number of the item installed by the vulnerability
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
	# @returns string
	#
	def name(self):
		return self.__name

	## Returns the description of the vulnerability
	# 
	# @returns string
	#
	def description(self):
		return self.__description
	
	## Returns what the vulnerability provides
	# 
	# @returns string
	#
	def provides(self):
		return self.__provides
	
	## Returns the version of what the vulnerabilty provides
	# 
	# @returns version - The version
	#
	def version(self):
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
	# @param provides_value (string) - The version string to test the vulnerability 
	# @param version_range (string) - The required version range of the dependency
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

## Stores and processes documentation of actions taken within the module
#		
class doc():
	
	## Create a doc object
	def __init__(self, module):
		self.__doc_list = []
		self.__module = module
	
	## Adds a line of documentation for a given vulnerability
	#
	# @param string vuln - The name of the vulnerability being documented	
	# @param string description - A description of actions taken
	#	
	def add_doc(self, vuln, description):
		if not cross_version.isstring(vuln):
			raise ValueError("Vulnerabilty value is not a string")
			
		if not cross_version.isstring(description):
			raise ValueError("Description value is not a string")
			
		self.__doc_list.append({"module": self.__module, "vulnerability": vuln, "description": description})

	def __encrypt_doc(self, key):
		pass
	
	## Returns all lines of documentation as a single string in the given format
	#
	# @param string output - Output type	
	#
	def get_all_docs(self, output="base64"):
		if output == 'clear':
			return self.__doc_to_string()
		elif output == 'base64':
			return self.__base64_doc()
		else:
			raise ValueError("Invalid output type")
		
	def __base64_doc(self):
		doc_string = self.__doc_to_string()
		
		if doc_string.strip() == "":
			return ""
		else:
			if cross_version.get_python_version() == 2:
				output = base64.standard_b64encode(doc_string)
			elif cross_version.get_python_version() == 3:
				output = base64.standard_b64encode(bytes(doc_string,'UTF-8'))
				output = output.decode('utf-8')
			else:
				assert False
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
		
		self.__tmp_version_restrictions = []
		self.__tmp_dependency_restrictions = []
		
		self.__commands_used_restrictions = []
		self.__commands_modified_restrictions = []
		
		self.__forced = []
		
		self.doc = doc(self.name())
		self.__difficulty = None
# Start abstract functions
	# Can't use Python abc functionality due to Python2/3 compatability
	
	## ABSTRACT: Returns the detailed name of the module
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
	#
	# @returns bool - Indicates if the vulnerabilities have run or not
	def run(self, options={}):
		raise NotImplementedError 
	
	# ABSTRACT: This function is called with a vulnerabilty object and values in the options for testing the functionality of module
	#~ def test_run(self, vuln_obj, options={}):
		#~ raise NotImplementedError 
	
# End abstract functions

	## Function for producing a blurb about the module
	#
	# @returns string - Short description of the module
	#
	def info(self):
		show_string = "\nName: " + self.name() + "\n\n"
		show_string += "Version: " + self.version() + "\n"
		show_string += "Author: " + self.author() + "\n\n"
		show_string += "Description:\n" + self.description() + "\n\n"
		return show_string

	## Allows access to create a new vulnerability object
	#
	# @param string name - Name of the new vulnerability. Commonly in all upper case _'s in place of spaces
	# @param string description - A short description of the vulnerability
	# @param string provides - A string that defines what service the vulnerability will provide. See documentation on "provides strings." Defaults to ''
	# @param string provides_version - Version of application indicated in the provides string
	# @returns vulnerability - New instance of a vulnerability object
	#
	def new_vulnerability(self, name, description, provides='', provides_version=''):
		return vulnerability(name, description, provides, provides_version)
	
	## Inserts a vulnerability object to the list of vulnerabilities provided by the module
	#
	# @param vulnerability vulnerability_obj - The vulnerability object to insert
	#
	def add_vulnerability(self, vulnerability_obj):
		if isinstance(vulnerability_obj, vulnerability):
			self.__vulnerability_list[vulnerability_obj.name()] = vulnerability_obj
		else:
			raise ValueError("Object is not an instance of vulnerability")
	
	## TESTING: Clears all vulnerabilities in the modules. Use only for testing 
	def clear_vulnerabilities(self):
		self.__vulnerability_list = {}
	
	## Get the vulnerabilities that will run. Call only after running get_vulnerabilities
	#
	# @returns vulnerability[] - List of vulnerabilities that are in the running list
	#
	def get_running_vulns(self):
		return copy.deepcopy(self.__running_vulns)
	
	## Return a vulnerability object by name. Used in module testing
	#
	# If the module does not exist, throws a ValueError
	#
	# @param string vuln_name - Name of the vulnerabilty to return
	# @returns vulnerabililty - The vulnerability instance that corresponds to the given name
	#
	def get_vulnerability_object(self, vuln_name):
		if not cross_version.isstring(vuln_name):
			raise ValueError("Name is not string")
		
		if vuln_name in self.__vulnerability_list:
			return self.__vulnerability_list[vuln_name]
		else:
			return False
	
	## Set if the module will return only one or one or more vulnerabilities
	#
	# @param Boolean - True = returns one or more vulnerabilities, False = returns only one vulnerability
	#
	def set_multi_vuln(self, value):
		if value == True or value == False:
			self.__multi_vuln = value
		else:
			raise ValueError("Invalid multi_vuln value")

# Functions for dependency resolution

	## Checks if the module contains a vulnerability that has the given provides string
	#
	# @param string search - Search value
	# @returns Boolean - True if the there is a vulnerabilty with the provides string, False if not
	#
	def has_provides(self, search):
		for vuln in self.__vulnerability_list:
			if self.__vulnerability_list[vuln].provides() == search:
				return True
		return False

	## Checks if the module contains a vulnerability that has the given difficulty level or lower
	#
	# @param object search - Search value
	# @returns Boolean - True if the there is a vulnerabilty with the difficulty level, False if not
	#
	def has_difficulty(self, search):
		
		if cross_version.isstring(search):
			search = convert_difficulty(search)
		
		if not cross_version.isinteger(search):
			raise ValueError("Invalid difficulty")
		
		for vuln in self.__vulnerability_list:
			if self.__vulnerability_list[vuln].get_difficulty() <= search or self.__vulnerability_list[vuln].get_difficulty() == None:
				return True
		
		return False


	## Returns the list of all vulnerabilities stored in the module
	#
	# @returns Map of vulnerability names to vulnerability object
	def vulnerability_list(self):
		return copy.deepcopy(self.__vulnerability_list)
		
	## Generates a list of vulnerabilities that fit within current restrictions
	#
	# @returns vulnerability[] - List of vulnerability objects
	#
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
				if not ver_restrict.version_pass(vuln.provides(), vuln.version()):
					valid = False
			
			# Restrict by dependency restrictions
			for dep_restrict in self.__dependency_restrictions:
				for dep in vuln.get_dependencies():
					if dep_restrict.provides_string() == dep.provides_string():
						if dep_restrict.range_pass(dep.provides_string(), dep.version_range()):
							valid = False
			
			
			# Restrict by version restrictions (Temporary entries)
			for ver_restrict in self.__tmp_version_restrictions:
				if not ver_restrict.version_pass(vuln.provides(), vuln.version()):
					valid = False
			
			# Restrict by dependency restrictions (Temporary entries)
			for dep_restrict in self.__tmp_dependency_restrictions:
				for dep in vuln.get_dependencies():
					if dep_restrict.provides_string() == dep.provides_string():
						if dep_restrict.range_pass(dep.provides_string(), dep.version_range()):
							valid = False
			
			# Restrict by OS
			if vuln.check_os_support() == False:
				valid = False
			
			if valid == True:
				valid_list.append(copy.deepcopy(vuln))
		
		return valid_list
	
	def test(self, vuln_name):
		
		if vuln_name not in self.__vulnerability_list:
			return False
		
		valid_list = self.__restricted_list()
		
		valid = False
		
		for i in range(len(valid_list)):
			if valid_list[i].name() == vuln_name:
				valid = True
				
		if valid == False:
			return False
		else:
			self.__running_vulns = [vuln_name]
			status = self.run()
			if status == True:
				print(self.doc.get_all_docs(output='clear'))
			
			return status
		
		
	# Generates a list of vulnerabilities that the module has selected for running based on current restrictions
	def __generate_vulnerabilities(self):
		
		valid_vulns = self.__restricted_list()
		return_list = []
		rand_gen = self.random()
		
		doing_none = False
		none_loc = -1 
		
		# Detect NONE vulnerability
		for i in range(len(valid_vulns)):
			if valid_vulns[i].name() == "NONE":
				none_loc = i
		
		if len(valid_vulns) == 0:
			return []
		else:
			# First check if well will remove the NONE vuln or only use NONE
			if none_loc != -1:
				if len(valid_vulns) == 1:
					return [valid_vulns[none_loc]]
				elif rand_gen.will_do() and rand_gen.will_do():
					return [valid_vulns[none_loc]]
				else:
					del valid_vulns[none_loc]
			
			if len(self.__forced) > 0:
				if self.__multi_vuln == False:
					for vuln in valid_vulns:
						if vuln.name() == self.__forced[0]:
							return [vuln]
				elif self.__multi_vuln == True:
					# If there are forced vulns, ensure they are inserted
					for forced in self.__forced:
						valid = False
						for vuln in valid_vulns:
							if vuln.name() == forced:
								valid = True
								return_list.append(vuln)
								
						if valid == False:
							return []
					
					# Possibly add extra vulnerabilities
					for vuln in valid_vulns:
						if not vuln.name() in self.__forced:
							if rand_gen.will_do():
								return_list.append(vuln)
					
			elif len(self.__forced) == 0: 	
				if self.__multi_vuln == True:
					while len(return_list) == 0:
						for vuln in valid_vulns:
							if rand_gen.will_do():
								return_list.append(vuln)
				elif self.__multi_vuln == False:
					vuln = rand_gen.array_random(valid_vulns)
					return_list.append(vuln)
			else:
				return_list = []

		return return_list
	
	## Returns a random list of vulnerabilities from the module that fit within current restrictions
	#
	# @returns vulnerability[] - List of vulnerability objects
	#
	def get_vulnerabilities(self, force=False):
		if len(self.__running_vulns) == 0 or force == True:
			self.__running_vulns = self.__generate_vulnerabilities()
			
		return copy.deepcopy(self.__running_vulns)
	
	## Sets the limit on the difficulty of vulnerabilities that can be returned
	#
	def set_difficulty_limit(self, limit):
		if not cross_version.isinteger(limit):
			raise ValueError("Difficulty limit must be integer format")
		
		if limit == 0:
			self.__difficulty = None
		else:
			self.__difficulty = limit 
	
	
	def _clear_temp_restrictions(self):
		self.__tmp_dependency_restrictions = []
		self.__tmp_version_restrictions = []
		
	def _add_temp_version_restriction(self, provides_string, version_range):
		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string must be a string")
			
		for restriction_item in self.__version_restrictions:
			if restriction_item.version_range() == version_range and restriction_item.provides_string() == provides_string:
				return
		
		self.__tmp_version_restrictions.append( version_restriction(provides_string, version_range) )
	
	
	## Restrict the use of certain dependencies temporarily (used in dependency resolution)
	def _add_temp_dependency_restriction(self, provides_string, version_range):
		
		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string must be a string")
			
		
		for restriction_item in self.__dependency_restrictions:
			if restriction_item.version_range() == version_range and restriction_item.provides_string() == provides_string:
				return
		
		self.__tmp_dependency_restrictions.append( dependency_restriction(provides_string, version_range) )
		
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

		
		self.__dependency_restrictions.append( dependency_restriction(provides_string, version_range) )
	
	def get_dependency_restrictions(self):
		return copy.deepcopy(self.__dependency_restrictions)
	
	def add_command_used_restrictions(self, command_used):
		self.__commands_used_restrictions.append(command_used)
	
	def add_command_modified_restrictions(self, command_modified):
		self.__commands_modified_restrictions.append(command_modified)

	## Set vulnerabilities that must be returned
	#
	# @param string[] forced_list - List of vulnerability names
	#
	def set_forced(self, forced_list):
		for item in forced_list:
			if item in self.__vulnerability_list:
				self.__forced.append(item)

		if self.__multi_vuln == False:
			self.__forced = [self.random().array_random(self.__forced)]
			
	## Returns the name of the current class. Used in dependency resolution
	#
	# @returns string - The name of the current class. Changes on inheritance
	#
	def get_class_name(self):
		return self.__class__.__name__

# Methods for returning useful functionality to modules
	def os_matches(self, type_string, flavor_string="*", version_string="*"):
		matcher = os_data.os_match(type_string, flavor_string, version_string)
		return self.os_info().matches(matcher)

	def os_info(self):
		return os_data.os_info()
		
	## Returns an instance of ba_random
	#
	# @returns Instance of ba_random
	#
	def random(self):
		return random_class()
	
	## Returns an instance of ba_random
	#
	# @param string filename - The name of the file
	# @returns Returns a simple_file instance initialized to the provided filename
	#	
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

	def network(self):
		return networking()
