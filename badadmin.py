import util.os_data as os_data
import util.cross_version as cross_version
import util.module_util as module_util
import os
import sys
import readline

NAME = "BadAdmin"
VERSION = "0.1dev"

def main():
	current_system = os_data.os_info()
	
	if not current_system.os_type() == os_data.OS.LINUX:
		print(NAME + " can currently only be run on Linux")
		
	running = True
	
	VALID_COMMANDS = [
		"exit",
		"quit",
		"help",
		"module",
		"run",
		"show",
		"set"
	]
	
	bd_vars = {
		"to_run": {"type": "list", "value": [], "description": ""},
		"base64": {"type": "bool", "value": True, "description": ""},
		"verbose": {"type": "bool", "value": False, "description": ""}
	}
	
	if not os.geteuid() == 0:
		print ("\nYou need to be root to run " + NAME)
		sys.exit()
	
	print("\n" + NAME + " " + VERSION + "\n")
	print("WARNING: Do not run this application on a production device!") 
	print("This application is intended to make things insecure.")
	print("DO NOT RUN IT ON A BOX THAT HAS STUFF YOU WANT TO KEEP SAFE!")
	
	while running == True:
		input_val = get_user_input("> ").strip()
		
		input_list = input_val.split(" ")
		
		command = input_list[0]
		
		if not command in VALID_COMMANDS and not command == "":
			print(command + ": invalid command")
		
		if command == "quit" or command == "exit":
			print("Exiting...")
			sys.exit()
		elif command == "module":
			if not len(input_list) > 1:
				print("Incomplete command")
				print("Valid sub-commands: add, remove, info, list")
			elif input_list[1] == "add":
				
				if not len(input_list) == 3:
					print(input_val + ": invalid command")
				else:
					module_name = input_list[2]
					if module_util.module_exists(module_name):
						if not module_name in bd_vars['to_run']['value']:
							bd_vars['to_run']['value'].append(module_name)
						else:
							print("Module is already set to be run")
						
					else:
						print("Module '" + module_name + "' does not exist")
				
				
			elif input_list[1] == "remove":
				print("remove")
			elif input_list[1] == "info":
				
				if not len(input_list) == 3:
					print(input_val + ": invalid command")
				else:
					module_name = input_list[2]
					if module_util.module_exists(module_name):
						tmp_module = module_util.import_module(module_name)
						print(tmp_module.info())
						
					else:
						print("Module '" + module_name + "' does not exist")
					
			elif input_list[1] == "list":
				module_list = module_util.list_modules()
				
				if len(module_list) > 0:
					for item in module_list:
						print("\t" + item)
				else:
					print("\nNo modules are installed!")
			else:
				print(input_val + ": invalid command")
				
		elif command == "run":
			if not len(bd_vars['to_run']['value']) > 0:
				print("\nERROR: No modules have been added. Cannot run\n")
			else:
				print ("\nAre you sure you want to run the modules? The changes made by " + NAME + " cannot be reversed!\nType 'yes' if you want to continue\n")
				
				answer = get_user_input("? ")
				
				if answer.strip() == "yes":
					print("Resolving module dependencies...")
					# Resolve dependencies
					print("Ordering modules for executing...")
					
					print("Executing modules...")
					
					print("Execution complete!")
					
				else:
					print("'yes' not given. Stopping...")  
				
		elif command == "show":
			if not len(input_list) > 1:
				print("Incomplete command")
				print("Valid sub-commands: vars, modules")
			elif input_list[1] == "vars":
				for var in bd_vars:
					print ("* " + var + "[" + bd_vars[var]['type'] + "] = " + str(bd_vars[var]['value']))
			elif input_list[1] == "modules":
				print("\nModules to be run:\n")
				for item in bd_vars['to_run']['value']:
					print(item)
			else:
				print(input_val + ": invalid command")
		elif command == "set":
			if not len(input_list) == 3:
				print("Incomplete command")
				print("Usage: set <variable name> <value>")
			else:
				if input_list[1] in bd_vars:
					
					key = input_list[1]
					value = input_list[2]
					success = True
					
					if bd_vars[key]['type'] == "bool" and not (value == "true" or value == "True" or value == "false" or value == "False"):
						print("Invalid value for bool type")
						success = False
					
					if success == True:
						if bd_vars[key]['type'] == "bool" and (value == "true" or value == "True"):
							bd_vars[key]['value'] = True
						elif bd_vars[key]['type'] == "bool" and (value == "false" or value == "False"):
							bd_vars[key]['value'] = False
						else:
							bd_vars[key]['value'] = value
					else:
						pass
				else:
					print("Invalid variable '" + input_list[1] + "'") 
def get_user_input(prompt):
	if cross_version.get_python_version() == 3:
		input_val = input(prompt)
	elif cross_version.get_python_version() == 2:
		input_val = raw_input(prompt)
	return input_val
	
main()
