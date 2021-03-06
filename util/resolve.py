## @package util.resolve
#
# Module that provides dependency resolution and prepares modules for operation
#
import util.cross_version as cross_version
import util.module_util as module_util
import modules.base as base
from util.ba_random import ba_random
import copy


## REMOVE FOR PRODUCTION
import inspect

## Maximum depth of dependencies before the resolver gives up. Keeps it from looping forever.
MAX_DEPTH = 25

## @class resolver
#
# Main class for dependency resolution
#
class resolver(object):
	
	## Create a new resolver object
	#
	def __init__(self, debug=False):
		
		self.__name_map = {} # Maps a module name to its object
		self.__parent_map = {} # Maps a module to its parents (all by name)
		self.__provides_map = {} # Maps a module to what it provides
		self.__vuln_map = {} # Maps a module's name to a list of vulnerability objects
		self.__processed = [] # List of processed vulnerabilities
		self.__load_restrictions = [] # List of modules that should not be attempted to load again
		
		self.__set_modules = [] # Lists modules that were added externally, not loaded during resolution
		
		self.__running = True # Flag if we are still running
		self.__restarting = False
		
		self.__done = False
		
		self.__faulting_modules = {}
		
		self.__depth = 0
		
		# 0 = no difficulty set, 1 = easy, 2 = medium, 3 = hard
		self.__difficulty = 0
		
		# Indicate if the process needs to be verbose
		self.__debug = debug
	
	## Set the difficulty limit for modules
	#
	# @param level (int) - The dofficulty level by numbers 1 - 3 (easy - hard)
	#
	def set_difficulty(self, level):
		if level >=0 and level <= 3:
			self.__difficulty == level
		else:
			raise ValueError("Invalid difficulty level")
	
	## Add a module to the resolver
	#
	# @param module (string|base_module) - Module name to add or module object to add		
	# @param forced (string[]) - List of vulnerability names that are forced for the module
	#
	def add_module(self, module, forced=[]):
		
		if issubclass(module.__class__, base.module_base):
			module_name = module.get_class_name()
		elif cross_version.isstring(module):
			module_name = module
		else:
			raise ValueError("Invalid module to add. Must be module object or name")
		
		if module_util.module_exists(module_name):
			
			if self.__debug:
				print("Adding module " + module_name)
			
			self.__insert_module(module_name, module_util.import_module(module_name))
			self.__set_modules.append(module_name)
			
			if len(forced) > 0:
				self.__name_map[module_name].set_forced(forced)
			
		else:
			return

	def __insert_module(self, module_name, module_obj):
		self.__name_map[module_name] = module_obj
		self.__name_map[module_name].set_difficulty_limit(self.__difficulty)

	## Start the dependency resolution
	#
	# @returns bool - True if successful, False if not
	#
	def start_resolve(self):
		
		if self.__debug:
			print("\n\n\n=======================================\nResolving module dependencies\n=======================================\n")
		
		name_list = list(self.__name_map.keys())
		
		if len(name_list) == 0:
			print("No modules added")
			return False
		
		pos = 0
		
		while self.__done == False:
			
			if self.__debug:
				print("At position " + str(pos))
				print("Processed: ")
				for name in self.__processed:
					print("\t" + name)
				
			if pos > len(name_list):
				print("Invalid state, pos is greater than loaded modules")
				return False
			
			initial_list = copy.deepcopy(self.__name_map)
			
			current_module = self.__name_map[name_list[pos]]
			
			result = self.__resolve_module(current_module, 1)
			
			# Delete name maps that are empty
			for name in copy.deepcopy(self.__name_map):
				if self.__name_map[name] == None:
					if self.__debug:
						print("Removing " + name)
					del self.__name_map[name]
					del self.__parent_map[name]
			
			end_list = copy.deepcopy(self.__name_map)
			name_list = list(self.__name_map.keys())
			
			if result == False:
				print("Error resolving.\nFaulting modules:")
				print(self.__faulting_modules)
				return False
			elif self.__restarting == True:
				if self.__debug:
					print("Full restart")
				self.__processed = []
				pos = 0
			elif not len(initial_list) == len(end_list):
				if self.__debug:
					print("Repositioning due to change in loaded modules") 
				pos = 0
			elif len(self.__processed) < len(name_list):
				pos += 1
			elif len(self.__processed) == len(name_list):
				done = True
				
				for module in self.__name_map:
					if not module in self.__processed:
						done = False
				
				if done == True:
					if self.__debug:
						print("Resolve complete")
					return True
				else:
					raise IndexError("Invalid location")
			else:
				raise IndexError("Invalid location")
				
	def __resolve_module(self, module_obj, depth, ver_restrictions=[], dep_restrictions=[]):
		
		front = "\t" * depth
		
		if self.__debug:
			print("\n\n" + front +  "Starting resolve for " + module_obj.name())
			print(front + "M: name_map: ")
			for name in self.__name_map:
				print(front + "\t" + name + ": " + str(self.__name_map[name]))
			print(front + "M: provides_map: " + str(self.__provides_map))
			print(front + "M: parent_map: " + str(self.__parent_map))
			print(front + "M: vuln_map: " + str(self.__vuln_map))
			print(front + "M: Processed: " + str(self.__processed))
			print(front + "M: Version Restrictions: " + str(ver_restrictions))
			print("\n")	
			
		
		# Insert restrictions here
		for ver_restrict in ver_restrictions:
			if module_obj.has_provides(ver_restrict.provides_string()):
				if self.__debug:
					print(front + "Adding restriction")
				module_obj.add_version_restriction(ver_restrict.provides_string(), ver_restrict.version_range())
		
		for dep_restrict in dep_restrictions:
			if module_obj.has_provides(dep_restrict.provides()):
				module_obj.add_version_restriction(dep_restrict.provides_string(), dep_restrict.version_range())	

		if depth + 1 >= MAX_DEPTH:
			self.__add_faulting_module(module_obj.get_class_name(), "Max depth exceeded!")
			return False
		elif self.__restarting == True:
			print("Restarting...")
			return False
		
		# Continue if the module has already been processed
		if module_obj.get_class_name() in self.__processed:
			if self.__debug:
				print(front + "Module " + module_obj.get_class_name() + " has already been processed!")
			return True
		
		 
		
		# Get vulnerabilities the module currently thinks are valid
		
		done = False
		
		while done == False:
			
			vuln_list = module_obj.get_vulnerabilities(force=True)

			
			if len(vuln_list) == 0:
				#~ self.__add_faulting_module(module_obj.get_class_name(), "Could not find usable vulnerabilities for module " + module_obj.get_class_name())
				if self.__debug:
					print(front + "M: No vulnerabilities found for module '" + module_obj.get_class_name() + "'")
				return False
			else:
				
				self.__vuln_map[module_obj.get_class_name()] = vuln_list
				
			

				vulns_status = True
				
				for vuln in vuln_list:

					result = self.__resolve_vuln(module_obj, depth, vuln, ver_restrictions, dep_restrictions)
					
					if result == False:
						module_obj.add_vuln_restriction(vuln.name());
					
					vulns_status = result and vulns_status
					
				if vulns_status == True:
					self.__processed.append(module_obj.get_class_name())
					return True
				else:
					if self.__debug:
						print("Vulnerabilities failed to resolve, trying again")

		return False	
								
	# Returns True if vulnerability successfully resolved, False if not		
	def __resolve_vuln(self, module_obj, depth, vuln_object, ver_restrictions=[], dep_restrictions=[]):			
		
		front = "\t   " * depth
		
		if self.__debug:
			print(front + "V: Processing " + module_obj.get_class_name() + "." + vuln_object.name())
			print(front + "------------------------------------------\n")
		
		dep_list = vuln_object.get_dependencies()
		
		if len(dep_list) > 0:

			for dep in dep_list:
				
				if self.__debug:
					print(front + "V: Dependency: ")
					for item in dep.get_links():
						print(front + "   " + str(item))

				dep_done = False
				# List for ORed vulnerabilities of provides strings that have failed
				failed_ps_list = [] 
				 
				
				# Loop until a valid module for the dependency is loaded
				while dep_done == False:

					
					selected_dep_ps = None
					selected_dep_range = None
					
					# Check if the dependency has mutiple matchable values (is OR)
					if dep.is_or():

						
						dep_choice_list = dep.get_links()
						
						dep_valid_list = []
						
						# Remove from the running any provides strings that have failed
						for dep_choice in dep_choice_list:
							if not dep_choice[0] in failed_ps_list:
								dep_valid_list.append(dep_choice)	
						
						# Check if the OR has failed on all counts, if so fail the vuln
						if len(dep_valid_list) == 0:
							return False
						
						# If so, check to see if any of the provides strings are already loaded, and use them if so
						for dep_choice in dep_valid_list:
							if dep_choice[0] in self.__provides_map:
								selected_dep_ps = dep_choice.provides_string
								selected_dep_range = dep_choice.version_range
								
						# If no existing values were found, then select a random one		
						if selected_dep_ps == None:
							choice_sel = ba_random().array_random(dep_valid_list)
							selected_dep_ps = choice_sel.provides_string
							selected_dep_range = choice_sel.version_range
					# If not OR, just get the strings
					else:
						link = dep.get_links()[0]
						selected_dep_ps = link.provides_string
						selected_dep_range = link.version_range
					
					if self.__debug:
						print(front + "V: Looking for a dependency that can provide: " + selected_dep_ps + " - " + str(selected_dep_range))
					
					# If no other module that provides the string, load a module that does
					if selected_dep_ps not in self.__provides_map:
						
						provides_done = False
						
						# Modules that were tried to provide the necessary provides_string, but failed to resolve
						failed_modules = []
						
						# Loop until we load a resolvable module that provides the given provides string
						while provides_done == False:
							
							# Get a module to attempt to use
							dep_module = self.__load_provides(selected_dep_ps, failed_modules)
							
							# Could not get a module that provides the dependency that works
							if dep_module == None:
								if dep.is_or():
									failed_ps_list.append(selected_dep_ps)
									provides_done = True
								else:
									self.__add_faulting_module("PS:" +  selected_dep_ps, "Could not load module for " + selected_dep_ps)
									return False
							else:
								
								if self.__debug:
									print(front + "V: Loaded module " + dep_module.get_class_name() + " to provide " + selected_dep_ps)
								
								self.__add_parent(module_obj.get_class_name(), dep_module.get_class_name())
							
								# Add the restriction given by the dependency definition
								dep_module.add_version_restriction(selected_dep_ps, selected_dep_range)
								
								result = self.__resolve_module(dep_module, depth + 1, ver_restrictions + module_obj.get_dependency_restrictions())
								
								if result == True:
									dep_done = True	
									provides_done = True							
								else:
									if self.__debug:
										print(front + "V: Module failed to resolve")
									if not dep_module in failed_modules:
										failed_modules.append(dep_module.get_class_name())
									self.__remove_child_tree(dep_module.get_class_name())
									dep_module._clear_restrictions()
									
					
					else:

						
						dep_done = True
						
						# A module with that provides string has been loaded and presumably processed. Use it
						provides_module = self.__name_map[self.__provides_map[selected_dep_ps]]
						
						# Check if dependency is parent to the dependency's parent (circular dependence)
						if self.__in_parent_path(module_obj.get_class_name() ,provides_module.get_class_name()):
							self.__add_faulting_module(module_obj.get_class_name(), "Circular dependency detected")
							return False
						
						# Check if the dependency module has already been processed
						if provides_module.get_class_name() in self.__processed:
							# If so, we need to check if we need to reprocess the tree
							
							# First create list of dependency restrictions that are for this dependency
							for dep_restriction in vuln.get_dependency_restrictions():
								if dep_restriction.provides_string() == self.__provides_map[selected_dep_ps]:
									provides_module._add_temp_dependency_restriction(dep_restriction)
							
							# Check if with the new restrictions the module doesn't need to be changed
							if provides_module.still_valid():
								# If so, convert the temp restictions into permanent ones
								provides_module.commit_temp_dependency_restrictions()
								# Clear the temp restrictions
								provides_module.clear_temp_dependency_restrictions()
							# If the vulnerabilities in the dependency are no longer possible, here's where things get interesting
							else:
								
								# First check if the module has any child modules (already processed dependencies)
								
								if self.__has_children(provides_module.get_class_name()):
									# If so, remove them
									self.__remove_child_tree(provides_module.get_class_name())
								
								# Check if the module is a dependency for anything else, because the vulnerabilities that it provided are now invalid
								if not self.__has_parents(provides_module.get_class_name()):
									# If not, things are a lot simpler
									
			
									# Add the current restrictions to the child module
									provides_module.commit_temp_dependency_restrictions()
									# Clear the temp restrictions
									provides_module.clear_temp_dependency_restrictions()
									# Reprocess the child module
									result = self.__resolve_module(provides_module, depth + 1)
									if result == False:
										return False

									
								else:
									# If not, we must figure out how to get both parent modules to give valid restrictions if possible
									# TODO: Change his algorithm to something better
									pass
									# Current Algorithm: Randomly select one of modules to set its current vulnerabilities and restrict them
									# This still has possibility of leaving out valid combinations, and also not working at all
									
									select_list = self.__parent_map[provides_module.get_class_name()] + [module_obj.get_class_name()]
									
									selection = ba_random().array_random(select_list)
									self.__name_map[selection].negate_selections()
									self.__restarting = True			
						else:
							error_message = "Invalid state, '" + selected_dep_ps +"' is set, but the module has not been resolved"
							self.__add_faulting_module(provides_module.get_class_name(), error_message)
							if self.__debug:
								print(error_message)
							return False
			
			
			return True
			
		else:
			return True	
							
				#~ resolve_result = self.__resolve_module(dep_module, depth + 1, ver_restrictions + module_obj.get_dependency_restrictions())

	
	# We must set a module to not done and any of its children
	def __remove_child_tree(self, parent):
		
		#~ print("Removing " + parent)
		
		# Remove the parent from the completed modules list
		if parent in copy.deepcopy(self.__processed):
			self.__processed.remove(parent)
		
		# Delete the module if it wasn't one that was set manually and it isn't a dependency for anything else
		#~ if not parent in self.__set_modules and not self.__has_parents(parent):
		if not parent in self.__set_modules:
			self.__name_map[parent] = None
		
		for item in copy.deepcopy(self.__provides_map):
			if self.__provides_map[item] == parent:
				del self.__provides_map[item]
		
		# Remove child modules
		temp_parent_map = copy.deepcopy(self.__parent_map)
		
		for child in temp_parent_map:
			if parent in temp_parent_map[child]:
				self.__parent_map[child].remove(parent)
				self.__remove_child_tree(child)		
				
	def __add_faulting_module(self, module, description):
		if not module in self.__faulting_modules:
			self.__faulting_modules[module] = description
	
	def __has_parents(self, child):
		if child not in self.__parent_map:
			return False
		else:
			if len(self.__parent_map[child]) == 0:
				return False
			else:
				return True
		return True
			
	def __has_children(self, parent):
		
		for child in self.__parent_map:
			for parent_map in self.__parent_map[child]:
				if parent_map == parent:
					return True
		return False
	
	# Add a parent to the child module
	def __add_parent(self, parent, child):
		if not child in self.__parent_map:
			self.__parent_map[child] = []
		
		self.__parent_map[child].append(parent)
		
	# Select a module that provides the given item and load it into the tree
	# Also set the provides_string to module mapping
	def __load_provides(self, provides_string, restriction_list):

		choose_list = []
		
		for module in module_util.get_module_list():
			
			current_module = module_util.import_module(module)

			if current_module.has_provides(provides_string) and current_module.get_class_name() not in restriction_list:
				
				# If the module we selected is already loaded (but not processed), use it
				if current_module.get_class_name() in self.__name_map and self.__name_map[current_module.get_class_name()] != None:
					self.__provides_map[provides_string] = current_module.get_class_name()
					return self.__name_map[current_module.get_class_name()]
				else:
					choose_list.append(module)

			
		if choose_list == 0:
			return None
		
		selected_module_name = ba_random().array_random(choose_list)
		
		selected_module = module_util.import_module(selected_module_name)
		
		if selected_module == None:
			return None
		
		
		
		# Set the provides mapping
		self.__provides_map[provides_string] = selected_module.get_class_name()
		
		self.__insert_module(selected_module.get_class_name(), selected_module)
		

		return self.__name_map[selected_module.get_class_name()]
	
	
	# Check if search is a parent or parent of parents. This would indicate a circular dependency
	def __in_parent_path(self, start, search):
		if not start in self.__parent_map:
			return False
		else:
			final_result = True
			for n in self.__parent_map[start]:
				if n == search:
					return True
				else:
					result = self.__in_parent_path(n, search)
					final_result = final_result and result
			return final_result
	
	def __get_children(self, parent):
		child_list = []
		
		for child in self.__parent_map:
			if parent in self.__parent_map[child]:
				child_list.append(child)
		
		return child_list
	
	def __order_modules(self, module_list, level):
		
		if self.__debug:
			front = "\t" * level
		
		module_map = {}
		temp_list = []
		
		all_used = []
		all_modified = []
		
		# Loop though each module in the list
		for module_name in module_list:
			
			if self.__debug:
				print(front + "(Before)Ordering: " + module_name)
				print(front + "(Before)module_map: " + str(module_map))
				
			# Get the current modules used and modified commands
			parent_obj = self.__name_map[module_name]
			parent_used = []
			parent_modified = []
			
			for vuln in self.__vuln_map[module_name]:
				parent_used += vuln.get_cmd_uses()
				parent_modified += vuln.get_cmd_modifies()
			
			all_used += parent_used
			all_modified += parent_modified
			
			parent_used = set(parent_used)
			parent_modified = set(parent_modified)
			
			# Get the commands used and modified by all children
			children_order, children_used, children_modified  = self.__order_modules(self.__get_children(module_name), level + 1)
			module_map[module_name] = {"list": children_order, "modified": children_modified, "used": children_used}
			
			parent_modified.union(children_modified)
			parent_used.union(children_used)
			
			if len(temp_list) == 0:
				temp_list.append(module_name)
			else:
				
				insert_pos = -1
				found_pos = False
				for i in range(len(temp_list)):
					current = module_map[temp_list[i]]
					
					if not parent_used.isdisjoint(current['modified']) and found_pos == False:
						insert_pos = i
						found_pos = True
					
					if not parent_modified.isdisjoint(current['used']) and found_pos == True:
						print("Used/Modified collision")
						return [], None, None

					
					if i == len(temp_list) - 1 and found_pos == False:
						insert_pos = len(temp_list)
			
				temp_list.insert(insert_pos, module_name)
			
			if self.__debug:
				print(front + "(After)Ordering: " + module_name)
				print(front + "(After)module_map: " + str(module_map))
			
		return_list = []
			
		# Extend the return list to include the child list
		for module in temp_list:
			return_list += module_map[module]['list'] + [module]
			
		return return_list, set(all_used), set(all_modified)
	
	## Returns a list of module names in order of operation
	#
	# @returns string[] - List of module names. Give as parameter to get_install_modules to get the objects.
	#		
	def get_install_order(self):
		
		if self.__debug:
			print("\n\n\n=======================================\nOrdering install\n=======================================\n")
		
		top_list = []
		
		# Get a list of highest level modules
		for module_name in self.__name_map:
			if not self.__has_parents(module_name):
				
				top_list.append(module_name)
		
		if self.__debug:
			print("Highest level modules: " + str(top_list) + "\n")
		ordered_list, modified_cmds, used_cmds = self.__order_modules(top_list, 0)
		
		return ordered_list
	
	## Returns a list of module names in order of operation
	#
	# @param module_list (string[]) - List of module names to get the objects of. Done in order
	# @returns modules[] - List of module objects
	#	
	def get_install_modules(self, module_list):
		
		return_list = []
		
		for module_name in module_list:
			return_list.append(self.__name_map[module_name])	
		
		return return_list
		
				
