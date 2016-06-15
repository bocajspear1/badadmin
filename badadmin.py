## @package badadmin
#
# User interface class and operation. This is the main module for BadAdmin
#

import util.os_data as os_data
import util.cross_version as cross_version
import util.module_util as module_util
import util.resolve as resolve
from util.ba_random import ba_random
import os
import sys
import traceback
## Name of the application
NAME = "BadAdmin Framework"
## Current version of the application
VERSION = "0.4"

## Valid commands for the interface
VALID_COMMANDS = [
		"exit",
		"quit",
		"help",
		"module",
		"run",
		"show",
		"set",
		"clear",
		"debug"
	]

## Stores help information for commands
HELP_TOPICS = {
	'exit': 'Exit BadAdmin',
	'quit': 'Exit BadAdmin',
	'help': 'Help with help?',
	'show': {
		'DEFAULT': 'Show variables and settings',
		'vars': 'Show BadAdmin enviroment variables',
		'modules': 'Show the modules that currently set to be run'
	},
	'set': {
		'DEFAULT': 'Set BadAdmin enviroment variables\n\nUsage: set <variable name> <value>'
	},
	'module': {
		"DEFAULT": "Adds, lists and removes modules",
		"test": "Test a vulnerability in a module. Can only be used in debug mode.\n\nUsage: module test <MODULE> <VULN_NAME>",
		"add": "Select a module to be run.\n\nUsage: module add <MODULE>",
		"remove": "Unselect a module to stop it from running\n\nUsage: module remove <MODULE>",
		"info": "Get more info on a module, including a list of vulnerabilities.\n\nUsage: module info <MODULE>",
		'random': "Get randomized vulnerabilities, selections based on the 'difficulty' variable",
		'force': "Force a particular vulnerability to run in a module.\n\nUsage: module force <MODULE> <VULN_NAME>"
	},
	'run': 'Execute all selected modules',
	'clear': 'Clears the screen',
	'debug': {
		"DEFAULT": "\nEnables or disables debug mode. \nValid options: on, off\n\nDebug mode does the following:\n * Makes all commands verbose\n * Stops 'run' from running the modules\n * Only shows dependency resolution during 'run'\n * Allows 'module test'",
		"on": "Turns debug mode on",
		"off": "Turns debug mode off"
	}
}

## @class badadmin.badadmin
# 
# User interface class
#
class badadmin():
	
	## Initialize the interface
	def __init__(self):
		current_system = os_data.os_info()
		
		if not current_system.os_type() == 'linux':
			print(NAME + " can currently only be run on Linux")
		
		if not os.geteuid() == 0:
			print ("\nYou need to be root to run " + NAME)
			sys.exit()
		
		self.__running = True
		self.__debug_mode = False
		
		self.__vars = {
			"to_run": {"type": "list", "value": [], "description": "Modules to be run"},
			"base64": {"type": "bool", "value": True, "description": "Sets if module output is Base64 encoded"},
			"verbose": {"type": "bool", "value": False, "description": "Sets if BadAdmin should be verbose"},
			"force": {"type": "map", "value": {}, "description": "Maps a module to vulnerabilities that will be forced to be run"},
			"level": {"type": "string", "value": 'any', "description": "Sets a limit to the difficulty level of modules", "limit": ['easy', 'medium', 'hard', 'any']}
		}
		
	def __warning(self):
		print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("! WARNING: Do not run this application on a production device!          !") 
		print("! This application is intended to make things INSECURE                  !")
		print("! DO NOT RUN IT ON A BOX THAT HAS STUFF YOU WANT TO KEEP SAFE!          !")
		print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")	
	
	def __show(self, options):
		if not len(options) == 1:
			print("Incomplete command")
			print("Valid sub-commands: vars, modules")
		else:
			subcommand = options[0]
			
			if subcommand == "vars":
				for var in self.__vars:
					print ("  + " + var + "[" + self.__vars[var]['type'] + "] = " + str(self.__vars[var]['value']) + " - " + self.__vars[var]['description'])
			elif subcommand == "modules":
				print("\nModules to be run:\n")
				for item in self.__vars['to_run']['value']:
					print(item)
			else:
				print("show: invalid subcommand + '" + subcommand + "'")
	
	def __set(self, options):
		if not len(options) == 2:
			print("set: Incomplete command")
			print("Usage: set <variable name> <value>")
		else:
			key = options[0]
			value = options[1]
			
			if key in self.__vars:
				success = True
				
				var_type = self.__vars[key]['type']
				
				if var_type == "bool":
					if value == "true" or value == "True" or value == "false" or value == "False":
						
						if value == "true" or value == "True":
							self.__vars[key]['value'] = True
						elif value == "false" or value == "False":
							self.__vars[key]['value'] = False
						else:
							print("Invalid!")
							
					else:
						print("Invalid value to type bool")
						
				elif var_type == "string":
					if "limit" in self.__vars[key] and not value in self.__vars[key]['limit']:
						print("Variable " + key + " must be from the following list: " + str(self.__vars[key]['limit']) )
					else:
						self.__vars[key]['value'] = value
				
			else:
				print("Variable '" + key + "' is invalid")
			
	def __help(self, options):
		if len(options) == 0:
			print("Available commands:")
			for command in VALID_COMMANDS:
				print("\t" + command)
			print("For help with commands, type 'help <COMMAND>'\n\n")
			print("Other help topics:")
			print("\tvulns\n\tvars\n")
		else:
			command = options[0]
			if not command in VALID_COMMANDS:
				print("Invalid command")
			else:
				if command in HELP_TOPICS:
					if cross_version.isstring(HELP_TOPICS[command]):
						print(command + ": " + HELP_TOPICS[command])
					elif "DEFAULT" in HELP_TOPICS[command] and len(options) == 1:
						print("\n" + command + ": " + HELP_TOPICS[command]["DEFAULT"] + "\n")
						if len(HELP_TOPICS[command]) > 1:
							print("\nSubcommands:\n")
							for sub in HELP_TOPICS[command]:
								if sub != 'DEFAULT':
									print("\t" + sub)
							print("\n")
					elif len(options) == 2:
						subcommand = options[1]
						if subcommand in HELP_TOPICS[command]:
							print("\n" + command + " " + subcommand + ": " + HELP_TOPICS[command][subcommand] + "\n")
						else:
							print("No help topics available")
						
					else:
						print("No help topics available")
	
	def __module(self, options):
		
		if len(options) == 0:
			print("Incomplete command")
			print("Valid sub-commands: add, remove, info, list, random, force, test")
		else:
			subcommand = options[0]
			del options[0]
			
			if subcommand == "add":
				
				if not len(options) == 1:
					print("module add: No module name")
				else:
					module_name = options[0]
					
					if module_util.module_exists(module_name):
						if not module_name in self.__vars['to_run']['value']:
							self.__vars['to_run']['value'].append(module_name)
							print("Module added")
						else:
							print("Module is already set to be run")
					else:
						print("Module '" + module_name + "' does not exist")
			elif subcommand == "random":	
				rand_list = []
				self.__vars['to_run']['value'] = []
				
				while len(rand_list) == 0:
				
					mod_list = module_util.get_module_list()
					
					set_level = self.__vars['level']['value']
					
					for module in mod_list:
						# Skip the test module
						if module == "test_module":
							continue
						
						mod_obj = module_util.import_module(module)
						
						if mod_obj:
							if set_level == "any":
								if ba_random().will_do():
									rand_list.append(module)
							else: 
								if mod_obj.has_difficulty(set_level) and ba_random().will_do():
									rand_list.append(module)
						else:
							print("Could not import module "+ module)
						
					
				for module_name in rand_list:
					self.__vars['to_run']['value'].append(module_name)		
						
			elif subcommand == "remove":
				if not len(options) == 1:
					print("module add: No module set")
				else:
					module_name = options[0]
					
					if module_util.module_exists(module_name):
						if module_name in self.__vars['to_run']['value']:
							self.__vars['to_run']['value'].remove(module_name)
							print("Module removed")
						else:
							print("Module is not set to run")
					else:
						print("Module '" + module_name + "' does not exist")			
			elif subcommand == "info":
				
				if not len(options) == 1:
					print("module info: No module name")
				else:
					module_name = options[0]
					
					if module_util.module_exists(module_name):
						tmp_module = module_util.import_module(module_name)
						print(tmp_module.info())
						
						print("Vulnerabilities:")
						for vuln in tmp_module.full_vulnerability_list():
							print("    " + vuln)
							
					else:
						print("Module '" + module_name + "' does not exist")	
			elif subcommand == "list":
				module_list = module_util.get_module_list()
				
				if len(module_list) > 0:
					for item in module_list:
						if item == "test_module":
							continue
						if item in self.__vars['to_run']['value']:
							print("\t+ " + item)
						else:
							print("\t- " + item)
				else:
					print("\nNo modules are set to run!")
			elif subcommand == "force":
				if not len(options) == 2:
					print("Enter a module and vulnerability to force")
				else:
					module = options[0]
					vuln = options[1]
					
					if module_util.module_exists(module):
						if vuln in module_util.import_module(module).full_vulnerability_list():
							if not module in self.__vars['force']['value']:
								self.__vars['force']['value'][module] = []
							
							if not vuln in self.__vars['force']['value'][module]:
								self.__vars['force']['value'][module].append(vuln)
							else:
								print("That vulnerability is already being forced")
						else:
							print("Module '" + module + "' does not have the vulnerability '" + vuln + "'")
					else:
						print("Module '" + module + "' does not exist")
			elif subcommand == "test":
				if self.__debug_mode == False:
					print("'module test' can only be used in debug mode")
				elif not len(options) == 2:
					print("Enter a module and vulnerability to test")
				else:
					module = options[0]
					vuln = options[1]
					
					if module_util.module_exists(module):
						module_obj = module_util.import_module(module)
						
						if vuln in module_obj.full_vulnerability_list():
							result = module_obj.test(vuln)
							if result == False:
								print("Test failed")
							else:
								print("Test succeeded")
						else:
							print("Module '" + module + "' does not have the vulnerability '" + vuln + "'")
					else:
						print("Module '" + module + "' does not exist")
			else:
				print("module: invalid subcommand '" + subcommand + "'")
			
	def __run(self, options):
		if not len(self.__vars['to_run']['value']) > 0:
			print("\nERROR: No modules have been added. Cannot run.\n")
		else:
			self.__warning()
			print ("\n\nAre you sure you want to run the modules? The changes made by " + NAME + " cannot be reversed!\nType 'yes' if you want to continue\n")
			
			answer = self.__user_input("? ")
			
			if answer == "yes":
				print("Resolving module dependencies...")
				
				resolver = None
				if self.__debug_mode == True:
					resolver = resolve.resolver(debug=True)
				else:	
					resolver = resolve.resolver()
					
				if not self.__vars['level']['value'] == 'any':
					resolver.set_difficulty(self.__vars['level']['value'])
				for module in self.__vars['to_run']['value']:
					if self.__vars['verbose']['value'] == True:
						print("\tAdding " + module)
					if module in self.__vars['force']['value']:
						resolver.add_module(module, forced=self.__vars['force']['value'][module])
					else:
						resolver.add_module(module)
						

				resolver.start_resolve()
				
				print("Ordering modules for executing...")
				order_list = resolver.get_install_modules(resolver.get_install_order())
				
				for module in order_list:
					if self.__vars['verbose']['value'] == True or self.__debug_mode == True:
						print("\tRunning " + module.name())
				
				print("Executing modules...")
				
				for module in order_list:
					if self.__vars['verbose']['value'] == True or self.__debug_mode == True:
						print("\tExecuting " + module.name())
						for vuln in module.get_running_vulns():
							print("\t  |-" + vuln.name())
					result = None
					
					if self.__debug_mode == False:
						result = module.run()
						if result == False:
							print("Module " + module.name() + " failed! Halting.")
							return
							
				if self.__debug_mode == False:
					print("Execution complete!")
					for module in order_list:
						print(module.doc.get_all_docs(output='clear'))
					
			else:
				print("'yes' not given. Stopping...")  
	
	def __debug(self, options):
		if len(options) == 0:
			print("Incomplete command")
			print("Valid options: on off")
		else:
			option = options[0].strip()
			
			if option == "on":
				print("Debugging mode on")
				self.__debug_mode = True
			elif option == "off":
				print("Debugging mode off")
				self.__debug_mode = False	
			else:
				print("Invalid option")
				
	def __user_input(self, prompt):
		try:
			input_val = ""
			if cross_version.get_python_version() == 3:
				input_val = input(prompt)
			elif cross_version.get_python_version() == 2:
				input_val = raw_input(prompt)
				
			return input_val.strip()
		except KeyboardInterrupt:
			return "exit"
			
	## Start the interface
	def start(self):
		print("""
______           _  ___      _           _       
| ___ \         | |/ _ \    | |         (_)      
| |_/ / __ _  __| / /_\ \ __| |_ __ ___  _ _ __  
| ___ \/ _` |/ _` |  _  |/ _` | '_ ` _ \| | '_ \ 
| |_/ / (_| | (_| | | | | (_| | | | | | | | | | |
\____/ \__,_|\__,_\_| |_/\__,_|_| |_| |_|_|_| |_|
""")
		print("\n" + NAME + " " + VERSION + "\n")
		self.__warning()
		
		while self.__running == True:
			try:
				if self.__debug_mode == True:
					user_input = self.__user_input("(debug)badadmin> ")
				else:
					user_input = self.__user_input("badadmin> ")
		
				input_list = user_input.split(" ")
				
				command = input_list[0]
				del input_list[0]
				
				if command == "":
					pass
				elif command == "ls":
					print("I'm not Linux...")
				elif command == "spare":
					print("...")
				elif not command in VALID_COMMANDS :
					print(command + ": invalid command")
				elif command == "quit" or command == "exit":
					print("Exiting...")
					sys.exit()
				elif command == "module":
					self.__module(input_list)
				elif command == "run":
					self.__run(input_list)
				elif command == "show":
					self.__show(input_list)
				elif command == "set":
					self.__set(input_list)
				elif command == "help":
					self.__help(input_list)
				elif command == "debug":
					self.__debug(input_list)
				elif command == "clear":
					print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
				else:
					print("Invalid command - " + command)
			except Exception as e:
				print("ERROR - Caught an error!!")
				print(e)
				traceback.print_exc()
## Main function of BadAdmin
def main():				
	bd = badadmin()
	bd.start()

main()		

