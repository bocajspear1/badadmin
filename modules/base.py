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
import collections

## REMOVE FOR PRODUCTION
#~ import inspect


Dependency_Choice = collections.namedtuple('Dependency_Choice', ['provides_string', 'version_range'])

## Adds the util folder to the import path of the module
def init():
	util_path = "./util"
	if not util_path in sys.path:
		sys.path.append(util_path)

## Convert a string difficulty to an numeric one
#
# @param difficulty (string) - String difficulty
# @returns int - Numeric difficulty
#
def convert_difficulty(difficulty):
	if difficulty == "easy":
		return 1
	elif difficulty == "medium":
		return 2
	elif difficulty == "hard":
		return 3
	else:
		raise ValueError("Invalid string for difficulty")

## Base class for restriction related classes (links and restrictions)
class restriction_base(object):

	## Create a new dependency base object. Don't directly create one of these.
	#
	def __init__(self, provides_string, version_range):

		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string is not a string")
		else:
			self.__provides_string = provides_string

		if cross_version.isstring(version_range):
			self.__version_range = version_util.version_range(version_range)
		elif isinstance(version_range, version_util.version_range):
			self.__version_range = version_range
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

	def __str__(self):
		return str(self.__class__) + "(" + self.__provides_string + "[" + str(self.__version_range) + "])"

## Represents a link between a vulnerability and possible modules that provide the required
# provides string
#
class dependency_link(object):
	def __init__(self, choice_list):

		#~ print("Choice List")
		#~ print(choice_list)
		#~ print(inspect.stack())
		self.__dep_links = []

		if len(choice_list) == 0:
			raise ValueError("No dependencies set")

		for choice in choice_list:

			if isinstance(choice, tuple) and len(choice) == 2 and cross_version.isstring(choice[0]) and cross_version.isstring(choice[1]):
				self.__dep_links.append(Dependency_Choice(choice[0], version_util.version_range(choice[1])))
			else:
				raise ValueError("Invalid tuple")

		self.__backup = copy.deepcopy(self.__dep_links)

	def get_links(self):
		return self.__dep_links

	def is_or(self):
		return len(self.__dep_links) > 1

	def restore(self):
		self.__dep_links = copy.deepcopy(self.__backup)

## Represents a restriction on the current modules vulnerabilities based on the
# version of an application they provide
class version_restriction(restriction_base):


	## Check if the provides string and version do not fall under the restriction
	#
	# @param provides_string (string) - The provides string to test
	# @param version_string (string|version) - The version (string or object) to test
	# @returns bool - True if the values match, False if not
	#
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
class dependency_restriction(restriction_base):

	## Check if the provides string and version range match the restriction
	#
	# @param provides_string (string) - The provides string to test
	# @param version_range (string|version_range) - The version range (string or object) to test
	# @returns bool - True if the values match, False if not
	#
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


	## Tests vulnerability version against a given version to see if the vulnerability
	# version falls within the bounds of the inputted version
	#
	# @param required_range (string)- The version string to test the vulnerability against
	# @returns bool - True if the vulnerabilty version passes, False if it does not
	#
	def is_in_range(self, required_range):

		if self.__version == None:
			return False

		if not isinstance(required_range, version_util.version_range):
			required_range = version_util.version_range(required_range)

		return required_range.in_range(self.__version)

	## Adds a dependency and its version range. Tuples can be used to make a logical OR.
	#
	# @param provides_value (tuple|list) - Tuple of list of tuples with the following format: (PROVIDES_STRING, VERSION_RANGE). Both values must be strings
	#
	def add_dependency(self, combos):

		if isinstance(combos, tuple):
			dep_item = dependency_link([combos])
		elif isinstance(combos, list):
			dep_item = dependency_link(combos)
		else:
			raise ValueError("Value must be a tuple or list of tuples")

		self.__dependencies.append(dep_item)

	## Returns a list of dependencies
	#
	# @returns string[] - List of dependencies
	#
	def get_dependencies(self):
		return copy.deepcopy(self.__dependencies)

	## Adds a link to the vulnerability. Usually a link to a page describing what the vulneraility
	# does.
	#
	# @param link (string) - The link to add
	#
	def set_link(self, link):
		if cross_version.isstring(link) and link.startswith("http://") or link.startswith("https://"):
			self.__link = link
		else:
			raise ValueError("Invalid link")

	## Returns the vulnerability link
	#
	# @returns string - The link
	#
	def get_link(self):
		return self.__link

	## Adds a command that the vulnerability uses to a list
	#
	# @param cmd (string) - The command to add
	#
	def add_cmd_uses(self, cmd):
		if cross_version.isstring(cmd):
			if not cmd in self.__cmd_uses:
				self.__cmd_uses.append(cmd)
		else:
			raise ValueError("Invalid command")

	## Adds a command that the vulnerability modifies to a list
	#
	# @param cmd (string) - The command to add
	#
	def add_cmd_modifies(self, cmd):
		if cross_version.isstring(cmd):
			if not cmd in self.__cmd_modifies:
				self.__cmd_modifies.append(cmd)
		else:
			raise ValueError("Invalid command")

	## Returns a list of commands the vulnerability uses
	#
	# @returns string[]
	#
	def get_cmd_uses(self):
		return copy.deepcopy(self.__cmd_uses)

	## Returns a list of commands the vulnerability modifies
	#
	# @returns string[]
	#
	def get_cmd_modifies(self):
		return copy.deepcopy(self.__cmd_modifies)

	## Add a supported OS to the vulnerability
	#
	# @param os_type (string) - The type of OS to match
	# @param flavor (string) - The flavor of the OS to match. Defaults to '*'
	# @param version (string) - The version of the OS to match. Defaults to '*'
	#
	def add_supported_os(self, os_type, flavor="*", version="*"):
		insert_os = os_data.os_match(os_type, flavor, version)
		self.__supported_os_list.append(insert_os)


	## Check if the vulnerability has support for the current system
	#
	# @returns bool - True if the system supports the vulnerability, False if not
	#
	def check_os_support(self):
		system_info = os_data.os_info()
		if len(self.__supported_os_list) == 0:
			return True

		for supported_os in self.__supported_os_list:
			if system_info.matches(supported_os):
				return True
		return False

	## Check if the vulnerability has support for the current system
	#
	# @param difficulty (string|int) - The difficulty to set for the vulnerabilty. 1 = easy to 3 = hard. String values of 'easy', 'medium' and 'hard' allowed.
	#
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

	## Gets the difficulty in number format
	#
	# @returns int - 1 = easy, 2 = medium, 3 = hard
	#
	def get_difficulty(self):
		return self.__difficulty

## Stores and processes documentation of actions taken within the module
#
class doc():

	## Create a doc object
	#
	# @param module (string) - The name of the module we are documenting for
	#
	def __init__(self, module):
		self.__doc_list = []
		self.__module = module

	## Adds a line of documentation for a given vulnerability
	#
	# @param vuln (string) - The name of the vulnerability being documented
	# @param description (string) - A description of actions taken
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
	# @param output (string)- Output type
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


	## Initialization
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

		self.__vuln_restrictions = []

		## The instance of the doc class for the module
		self.doc = doc(self.name())

		self.__difficulty = None
# Start abstract functions
	# Can't use Python abc functionality due to Python2/3 compatability

	## ABSTRACT: Returns the detailed name of the module
	#
	# @returns string - Long name of the module
	#
	def name(self):
		raise NotImplementedError

	## ABSTRACT: Returnes the version of the module. NOT related to any version of application the module installs
	#
	# @returns string - Version of the module
	#
	def version(self):
		raise NotImplementedError

	## ABSTRACT: Returns the author of the module
	#
	# @returns string - Author of the module
	#
	def author(self):
		raise NotImplementedError

	## ABSTRACT: Returns a description of the module
	#
	# @returns string - A description of the module
	#
	def description(self):
		raise NotImplementedError

	## ABSTRACT: Function for when the vulnerabilities are run
	#
	# @returns bool - Indicates if the vulnerabilities have run or not
	#
	def run(self, options={}):
		raise NotImplementedError

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
	# @param name (string) - Name of the new vulnerability. Commonly in all upper case _'s in place of spaces
	# @param description (string) - A short description of the vulnerability
	# @param provides (string) - A string that defines what service the vulnerability will provide. See documentation on "provides strings." Defaults to ''
	# @param provides_version (string) - Version of application indicated in the provides string
	# @returns vulnerability - New instance of a vulnerability object
	#
	def new_vulnerability(self, name, description, provides='', provides_version=''):
		return vulnerability(name, description, provides, provides_version)

	## Inserts a vulnerability object to the list of vulnerabilities provided by the module
	#
	# @param vulnerability_obj (vulnerability) - The vulnerability object to insert
	#
	def add_vulnerability(self, vulnerability_obj):
		if isinstance(vulnerability_obj, vulnerability):
			self.__vulnerability_list[vulnerability_obj.name()] = vulnerability_obj
		else:
			raise ValueError("Object is not an instance of vulnerability")

	## TESTING: Clears all vulnerabilities in the modules. Use only for testing
	def clear_vulnerabilities(self):
		self.__vulnerability_list = {}

	## Get the vulnerabilities that will run. Call only after running get_vulnerabilities. Used in modules during the 'run' method
	#
	# @returns vulnerability[] - List of vulnerabilities that are in the running list
	#
	def get_running_vulns(self):
		return copy.deepcopy(self.__running_vulns)

	## Return a vulnerability object by name. Used in module testing
	#
	# If the module does not exist, throws a ValueError
	#
	# @param vuln_name (string) - Name of the vulnerabilty to return
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
	# @param value (bool) - True = returns one or more vulnerabilities, False = returns only one vulnerability
	#
	def set_multi_vuln(self, value):
		if value == True or value == False:
			self.__multi_vuln = value
		else:
			raise ValueError("Invalid multi_vuln value")

	## Return if the module is set to return more than one vulnerability
	#
	# @return bool
	#
	def is_multi_vuln(self):
		return self.__multi_vuln == True

# Functions for dependency resolution

	## Checks if the module contains a vulnerability that has the given provides string
	#
	# @param search (string) - Search value
	# @returns bool - True if the there is a vulnerabilty with the provides string, False if not
	#
	def has_provides(self, search):
		for vuln in self.__vulnerability_list:
			if self.__vulnerability_list[vuln].provides() == search:
				return True
		return False

	## Checks if the module contains a vulnerability that has the given difficulty level or lower
	#
	# @param search (string|int) - Search value
	# @returns bool - True if the there is a vulnerabilty with the difficulty level, False if not
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
	# @returns dict - Map of vulnerability names to vulnerability object
	#
	def full_vulnerability_list(self):
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
			#~ print("Starting: " + str(len(self.__vulnerability_list)))
			valid = True

			# Restrict by name
			if vuln_name in self.__vuln_restrictions:
				valid = False

			# Restrict by difficulty
			if not self.__difficulty == None:
				if not vuln.get_difficulty() <= self.__difficulty:
					valid = False

			# Restrict by version restrictions
			for ver_restrict in self.__version_restrictions:
				if not ver_restrict.version_pass(vuln.provides(), vuln.version()):
					valid = False

			# Restrict by dependency restrictions
			for dep in vuln.get_dependencies():
				for dep_restrict in self.__dependency_restrictions:
					for choice in copy.deepcopy(dep.get_links()):
						if dep_restrict.provides_string() == choice.provides_string:
							if dep_restrict.range_pass(choice.provides_string, choice.version_range):
								dep.get_links().remove(choice)
				if len(dep.get_links()) == 0:
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

	## Test a given vulnerability by only selecting the vulnerability and calling 'run'. Will print out any documentation made
	#
	# @param vuln_name (string) - The name of the vulnerability to test
	# @returns bool - True if successful, False if not
	#
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


	# Do the selection process of vulnerabilities from the list of valid vulns
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

						# If a forced vuln is not found, return blank
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
	# @param limit (int) - Limit in number format
	#
	def set_difficulty_limit(self, limit):
		if not cross_version.isinteger(limit):
			raise ValueError("Difficulty limit must be integer format")

		if limit == 0:
			self.__difficulty = None
		else:
			self.__difficulty = limit

	def _clear_restrictions(self):
		self.__version_restrictions = []
		self.__dependency_restrictions = []

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


	## Restrict the use of a vulnerability by name
	def add_vuln_restriction(self, vuln_name):
		if vuln_name in self.__vulnerability_list:
			self.__vuln_restrictions.append(vuln_name)
		else:
			raise ValueError("Invalid vulnerability name")

	## Restrict the use of certain dependencies temporarily (used in dependency resolution)
	def _add_temp_dependency_restriction(self, provides_string, version_range):

		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string must be a string")


		for restriction_item in self.__dependency_restrictions:
			if restriction_item.version_range() == version_range and restriction_item.provides_string() == provides_string:
				return

		self.__tmp_dependency_restrictions.append( dependency_restriction(provides_string, version_range) )

	## Restrict what version range can be returned
	#
	# @param provides_string (string) - Provides string to restrict
	# @param version_range (string|version_range) - version range to restrict
	#
	def add_version_restriction(self, provides_string, version_range):

		if not cross_version.isstring(provides_string):
			raise ValueError("Provides string must be a string")

		for restriction_item in self.__version_restrictions:
			if restriction_item.version_range() == version_range and restriction_item.provides_string() == provides_string:
				return

		self.__version_restrictions.append( version_restriction(provides_string, version_range) )

	## Restrict the use of certain dependencies
	#
	# @param provides_string (string) - Prrovides string to restrict
	# @param version_range (string|version_range) - version range to restrict
	#
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

	## Get a list of module's dependency restrictions
	#
	# @returns dependency_restriction[]
	#
	def get_dependency_restrictions(self):
		return copy.deepcopy(self.__dependency_restrictions)

	## Add a command used restriction to the module
	#
	# @param command_used (string) - Command to restrict
	#
	def add_command_used_restrictions(self, command_used):
		self.__commands_used_restrictions.append(command_used)

	## Add a command modified restriction to the module
	#
	# @param command_modified (string) - Command to restrict
	#
	def add_command_modified_restrictions(self, command_modified):
		self.__commands_modified_restrictions.append(command_modified)

	## Set vulnerabilities that must be selected
	#
	# @param forced_list (string[]) - List of vulnerability names
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

	## Attempt to remove a vulnerability from the running vulns
	# Returns a status based on whether or not the remove will create a valid state
	# for the module for not. e.g. does not remove a forced vulnerability or make the
	# running list empty.
	#
	def remove_vulnerability(self, vuln_name):
		if vuln_name in self.__forced:
			return False
		else:
			del_loc = -1

			for i in range(len(self.__running_vulns)):
				vuln = self.__running_vulns[i]
				if vuln.name() == vuln_name:
					del_loc = i

			if del_loc != -1:
				if len(self.__running_vulns) - 1 == 0:
					return False
				else:
					del self.__running_vulns[del_loc]
			else:
				print("Vulnerability " + vuln_name + " is not being run")
				return True


# Methods for returning useful functionality to modules
	## Sees if the the current system matches the given values
	#
	# @param type_string (string) - The OS type to match the system to
	# @param flavor_string (string) - The flavor of the OS type to match the system to. Defaults to '*'
	# @param version_string (string) - The version of the OS type to match the system to. Defaults to '*'
	# @returns bool - Result of the match. True if the system matches, False if not
	#
	def os_matches(self, type_string, flavor_string="*", version_string="*"):
		matcher = os_data.os_match(type_string, flavor_string, version_string)
		return self.os_info().matches(matcher)

	## Returns an instance of the os_info class
	#
	# @returns os_info - os_info instance
	#
	def os_info(self):
		return os_data.os_info()

	## Returns an instance of ba_random
	#
	# @returns ba_random
	#
	def random(self):
		return random_class()

	## Returns an simple_file object of a given file
	#
	# @param filename (string) - The name of the file
	# @returns simple_file - instance initialized to the provided filename
	#
	def file(self, filename):
		return simple_file(filename)

	## Returns an simple_dir object of the given directory
	#
	# @param dirname (string) - The name of the directory
	# @returns simple_dir - Instance initialized to the provided name
	#
	def dir(self, dirname):
		return simple_dir(dirname)

	## Returns a simple_command object
	#
	# @returns simple_command
	#
	def command(self):
		return simple_command()

	## Gives access to cross_version module
	#
	# @returns cross_version access
	#
	def cross_version(self):
		return cross_version

	## Returns a package_manager object
	#
	# @returns package_manager - Initialized
	#
	def package_manager(self):
		return simple_packages()

	## Returns a network object
	#
	# @returns network - Initialized
	#
	def network(self):
		return networking()

	def storage_file(self, name):
		storage_path = "./modules/" + self.get_class_name() + "/storage/"
		sf = simple_file(storage_path + name)
		if sf.exists():
			return sf
		else:
			return False
