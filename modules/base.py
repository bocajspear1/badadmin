import os
import random
import util.cross_version as cross_version
import util.version_string as version_string
import copy
import sys
#import subprocess
from util.simple_filesystem import simple_file
from util.simple_filesystem import simple_dir
from util.simple_command import simple_command
import util.os_data as os_data
import base64

#PYTHON_VERSION = sys.version_info.major



## Represents a link between a vulnerability and possible vulnerailities
# that provide the requested service or application
#
#
class dependency_link(object):
	
	def __init__(self, provides_string, version_range):
		
		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string is not a string")
		else:
			self.__provides_string = provides_string
		
		if not version_string.is_range(version_range):
			raise ValueError("Version range is not a valid range")
		else:
			self.__version_range = version_range
	
	
	def provides_string(self):
		return copy.deepcopy(self.__provides_string)
		
	def version_range(self):
		return copy.deepcopy(self.__version_range)

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
		self.__provides = provides
		self.__version = provides_version
		self.__dependencies = []
		self.__cmd_uses = []
		self.__cmd_modifies = []

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
		return self.__version
	
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
	def compare_version(self, version):
		return version_string.compare_version(version, self.__version)
	
	## Tests vulnerability version against a given version to see if the vulnerability
	# version falls within the bounds of the inputted version
	#
	# @param {string} required_range - The version string to test the vulnerability against
	# @returns {boolean} = True if the vulnerabilty version passes, False if it does not
	#
	def test_required_range(self, required_range):
		return version_string.test_range(required_range, self.__version)
	
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

	
	def add_support_os_flavor(self, flavor):
		pass

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
		self.__supported_os_list = []
		self.doc = doc()
		self.OS = os_data.OS
		self.LINUX = os_data.LINUX
		
	# Start abstract functions
	# Can't use Python abc functionality due to Python2/3 compatability
	
	## Returns the name of the module
	def name(self):
		raise NotImplementedError 
	
	## Returnes the version of the module. NOT related to any version of application the module installs
	def version(self):
		raise NotImplementedError 
	
	## Returns the author of the module
	def author(self):
		raise NotImplementedError 
	
	## Returns a description of the module
	def description(self):
		raise NotImplementedError 
		
	## Function for when the vulnerabilities are run
	def run(self, options={}):
		raise NotImplementedError 
	
	def info(self):
		show_string = "\nName: " + self.name() + "\n\n"
		show_string += "Version: " + self.version() + "\n"
		show_string += "Author: " + self.author() + "\n\n"
		show_string += "Description:\n" + self.description() + "\n\n"
		return show_string
	
	## Function for when a vulnerability is tested
	def test_run(self, vuln_obj, options={}):
		raise NotImplementedError 
	
	# End abstract functions
	
	## Get a vulnerability object from the list and return it
	def get_test_vuln(self, vuln_name):
		pass
				
	## Allows access to create a new vulnerability object
	#
	def _new_vulnerability(self, name, description, provides='', provides_version=''):
		return vulnerability(name, description, provides, provides_version)
		
	def _add_vulnerability(self, vulnerability_obj):

		if isinstance(vulnerability_obj, vulnerability):
			self.__vulnerability_list[vulnerability_obj.get_name()] = vulnerability_obj
		else:
			raise ValueError("Object is not an instance of vulnerability")
	
	def get_vulnerability_object(self, vuln_name):
		
		if not cross_version.isstring(vuln_name):
			raise ValueError("Name is not string")
		
		if vuln_name in self.__vulnerability_list:
			return self.__vulnerability_list[vuln_name]
		else:
			return False
	
	## Generates a a list of one or more vulnerabilities	
	def generate_vulnerability_list(self):
		if len(self._vulnerability_list) == 0:
			return []
		else:
			pass
	
	def get_os_info(self):
		pass
	
	def set_multi_vuln(self, value):
		if value == True or value == False:
			self.__multi_vuln = value
			
		else:
			raise ValueError("Invalid multi_vuln value")

# Functions for dependency resolution
	def has_provides(self, search):
		for vuln in self.vulnerabilities:
			if vuln.get_provides() == search:
				return True
		
		return False


	
		
	def file(self, filename):
		return simple_file(filename)
		
	def dir(self, dirname):
		return simple_dir(dirname)	

	def command(self):
		return simple_command()

	def cross_version(self):
		return cross_version
