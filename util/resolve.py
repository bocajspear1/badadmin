import util.cross_version as cross_version
import util.module_util as module_util
import modules.base as base
from util.ba_random import ba_random
import copy

MAX_DEPTH = 25

class resolver(object):
	
	def __init__(self, debug=False):
		
		self.__name_map = {} # Maps a module name to its object
		self.__parent_map = {} # Maps a module to its parents (all by name)
		self.__provides_map = {} # Maps a module to what it provides
		self.__vuln_map = {} # Maps a module's name to a list of vulnerability objects
		self.__processed = [] # List of processed vulnerabilities
		
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
	
	def set_difficulty(self, level):
		if level >=0 and level <= 3:
			self.__difficulty == level
		else:
			raise ValueError("Invalid difficulty level")
			
	def add_module(self, module):
		
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
			
		else:
			return

	def __insert_module(self, module_name, module_obj):
		self.__name_map[module_name] = module_obj
		self.__name_map[module_name].set_difficulty_limit(self.__difficulty)
		
		self.__set_modules.append(module_name)

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
				print("Proccesed: " + str(self.__processed))
				
			if pos > len(name_list):
				print("Invalid state, pos is greater than loaded modules")
				return False
			
			initial_list = copy.deepcopy(self.__name_map)
			
			current_module = self.__name_map[name_list[pos]]
			
			result = self.__resolve_module(current_module, 0)
			
			# Delete name maps that are empty
			for name in self.__name_map:
				if self.__name_map[name] == None:
					del self.__name_map[name]
			
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
		
		front = "  " * depth
		
		if self.__debug:	
			print(front + "Version Restrictions: " + str(ver_restrictions))
		
		# Insert restrictions here
		for ver_restrict in ver_restrictions:
			if module_obj.has_provides(ver_restrict.provides_string()):
				if self.__debug:
					print(front + "Adding restriction")
				module_obj.add_version_restriction(ver_restrict.provides_string(), ver_restrict.version_range())
		
		for dep_restrict in dep_restrictions:
			if module_obj.has_provides(dep_restrict.get_provides()):
				module_obj.add_version_restriction(dep_restrict.provides_string(), dep_restrict.version_range())	
		
		
		
		if depth + 1 >= MAX_DEPTH:
			self.__add_faulting_module(module_obj.get_class_name(), "Max depth exceeded!")
			return False
		elif self.__restarting == True:
			return False
		
		
		vuln_list = module_obj.get_vulnerabilities()
		
		if len(vuln_list) == 0:
			self.__add_faulting_module(module_obj.get_class_name(), "Could not find usable vulnerabilities for module " + module_obj.get_class_name())
			return False
		elif module_obj.get_class_name() in self.__processed:
			if self.__debug:
				print(front + "Module " + module_obj.get_class_name() + " has already been processed!")
			return True
		else:
			if self.__debug:
				print("\n\n" + front +  "Starting resolve for " + module_obj.name())
				print(front + "name_map: " + str(self.__name_map))
				print(front + "provides_map: " + str(self.__provides_map))
				print(front + "parent_map: " + str(self.__parent_map))
				print(front + "vuln_map: " + str(self.__vuln_map))
				print(front + "processed: " + str(self.__processed))
				print("\n")
			
			dep_result = True
			
			self.__vuln_map[module_obj.get_class_name()] = vuln_list
			
			for vuln in vuln_list:
				
				if self.__debug:
					print(front + "Processing " + module_obj.get_class_name() + "." + vuln.get_name())

				dep_list = vuln.get_dependencies()
				if len(dep_list) == 0:
					pass
				else:
					# For each dependency, look for modules that provide the necessary items
					for dep in dep_list:
						
						# If the module loaded has the provides string, and the module has not yet been loaded, load it
						if dep.provides_string() not in self.__provides_map:
							dep_module = self.__load_provides(dep.provides_string())
							
							if dep_module == False:
								self.__add_faulting_module("PS:" +  dep.provides_string(), "Could not load module for " + dep.provides_string())
								return False
							
							self.__add_parent(module_obj.get_class_name(), dep_module.get_class_name())
							
							
							dep_module.add_version_restriction(dep.provides_string(), dep.version_range().get_string())
							result = self.__resolve_module(dep_module, depth + 1, ver_restrictions + module_obj.get_dependency_restrictions())
							dep_result = dep_result and result
						else:
							# A module with that provides string has been loaded and presumably processed. Use it
							provides_module = self.__name_map[self.__provides_map[dep.provides_string()]]
							
							# Check if dependency is parent to the dependency's parent (circular dependence)
							if self.__in_parent_path(module_obj.get_class_name() ,provides_module.get_class_name()):
								self.__add_faulting_module(module_obj.get_class_name(), "Circular dependency detected")
								return False
							
							# Check if the dependency module has already been processed
							if provides_module.get_class_name() in self.__processed:
								# If so, we need to check if we need to reprocess the tree
								
								
								# First create list of dependency restrictions that are for this dependency
								for dep_restriction in vuln.get_dependency_restrictions():
									if dep_restriction.provides_string() == self.__provides_map[dep.provides_string()]:
										provides_module.add_temp_dependency_restriction(dep_restriction)
								
								# Check if with the new restrictions the module doesn't need to be changed
								if provides_module.still_valid():
									# If so, convert the temp restictions into permanent ones
									provides_module.commit_temp_dependency_restrictions()
									# Clear the temp restrictions
									provides_module.clear_temp_dependency_restrictions()
									dep_result = dep_result and True
								# If the vulnerabilities in the dependency are no longer possible, here's where things get interesting
								else:
									
									# First check if the module has any child modules (already processed dependencies)
									
									if self.__has_children(provides_module.get_class_name()):
										# If so, remove them
										self.__remove_child_tree(provides_module.get_class_name())
									
									# Check if the module is a dependency for anything else
									if not self.__has_parents(provides_module.get_class_name()):
										# If not, things are a lot simpler
										
				
										# Add the current restrictions to the child module
										provides_module.commit_temp_dependency_restrictions()
										# Clear the temp restrictions
										provides_module.clear_temp_dependency_restrictions()
										# Reprocess the child module
										result = self.__resolve_module(provides_module, depth + 1)
										dep_result = dep_result and result
										
									else:
										# If not, we must figure out how to get both parent modules to give valid restrictions if possible
										# TODO: Change his algorithm to something better
										pass
										# Current Algorithm: Randomly select one of modules to set its current vulnerabilities and restrict them
										# This still has possibility of leaving out valid combinations, and also not working at all
										
										select_list = self.__parent_map[provides_module.get_class_name()] + [module_obj.get_class_name()]
										
										selection = ba_random.array_random(select_list)
										self.__name_map[selection].negate_selections()
										self.__restarting = True
										
											
							else:
								self.__add_faulting_module(provides_module.get_class_name(), "Invalid state, if a module is set as provides, it should be processed")
								return False
								
						resolve_result = self.__resolve_module(dep_module, depth + 1, ver_restrictions + module_obj.get_dependency_restrictions())
			
			self.__processed.append(module_obj.get_class_name())
			return dep_result
	
	# We must set a module to not done and any of its children
	def __remove_child_tree(self, parent):
		
		# Remove the parent from the completed modules list
		self.__processed.remove(parent)
		
		# Delete the module if it wasn't one that was set manually and it isn't a dependency for anything else
		if not parent in self.__set_modules and not self.__has_parents(parent):
			self.__name_map[parent] = None
		
		
		# Remove child modules
		temp_parent_map = copy.deepcopy(self.__parent_map)
		
		for child in temp_parent_map:
			if parent in temp_parent_map[child]:
				self.__parent_map[child].remove(parent)
				self.__remove_child_tree(self, child)		
				
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
	def __load_provides(self, provides_string):
		
		choose_list = []
		
		for module in module_util.get_module_list():
			current_module = module_util.import_module(module)
			if current_module.has_provides(provides_string):
				
				# If the module we selected is already loaded (but not processed), use it
				if current_module.get_class_name() in self.__name_map:
					self.__provides_map[provides_string] = current_module.get_class_name()
					return self.__name_map[current_module.get_class_name()]
				else:
					choose_list.append(module)
		
		selected_module_name = ba_random().array_random(choose_list)
		
		selected_module = module_util.import_module(selected_module_name)
		
		if selected_module == False:
			return False
		
		if self.__debug:
			print("Loaded module " + selected_module.get_class_name() + " to provide " + provides_string)
		
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
			front = "  " * level
		
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
					current = module_map[install_order[i]]
					
					if parent_used.isdisjoint(current['modified']) and found_pos == False:
						insert_pos = i
					elif not parent_used.isdisjoint(current['modified']):
						insert_pos = i
						found_pos = True
					
					if not current['modified'].isdisjoint(r_item['used']) and found_pos == True:
						print("Used/Modified collision")
						return [], None, None
					
					if i == len(temp_list) - 1 and found_pos == False:
						insert_pos = len(temp_list)
			
				temp_list.insert(insert_pos, parent)
			
			if self.__debug:
				print(front + "(After)Ordering: " + module_name)
				print(front + "(After)module_map: " + str(module_map))
			
		return_list = []
			
		# Extend the return list to include the child list
		for module in temp_list:
			return_list += module_map[module]['list'] + [module]
			
		return return_list, set(all_used), set(all_modified)
			
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
		
		
	def __get_child_lists(self, parent):
		child_list = self.__get_children(parent)
		
		parent_obj = self.__name_map[parent]
		parent_used = []
		parent_modified = []
		
		for vuln in self.__vuln_map[parent]:
			parent_used += vuln.get_cmd_uses()
			parent_modified += vuln.get_cmd_modifies()
			
		parent_used = set(parent_used)
		parent_modified = set(parent_modified)
		
		
		child_map = {}
		child_list = []
		
		for child in child_list:
			ordered_list, modified_cmds, used_cmds = self.__get_child_lists(child)
			parent_modified.union(modified_cmds)
			parent_used.union(used_cmds)
			child_map[child] = {"list": ordered_list, "modified": modified_cmds, "used": used_cmds}
			if len(return_list) == 0:
				return_list.append(child)
			else:
				
				insert_pos = -1
				
				for i in range(len(return_list)):
					r_item = child_map[return_list[i]]
					current = child_map[child]
					
					if current['used'].isdisjoint(r_item['modified']) and insert_pos == -1:
						insert_pos = i
					
					if not current['modified'].isdisjoint(r_item['used']):
						print("Used/Modified collision")
						return [], None, None
					
					if i == len(return_list) - 1:
						insert_pos = len(return_list)
					
					
								
				if insert_pos == -1:
					print("Could not insert into install order")
					return [], None, None
				else:
					return_list.insert(insert_pos, child)
					
		child_set = set(parent).union(set(child_list))
			
		return child_set, parent_modified, parent_used
				
