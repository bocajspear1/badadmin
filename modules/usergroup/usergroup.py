# Import the base module
from ..base import module_base

class usergroup(module_base):
	
	def __init__(self):
		super(usergroup, self).__init__()
		
		passwd_vuln = self._new_vulnerability('USERGROUP_WEAK_PASSWORD', 'Changes the passwords of users to a weak one')
		passwd_vuln.add_cmd_uses('passwd')
		passwd_vuln.set_difficulty('hard')
		
		self._add_vulnerability(passwd_vuln)
		
		extra_user = self._new_vulnerability('USERGROUP_EXTRA_USERS', 'Adds extra users that can log in')
		extra_user.add_cmd_uses('useradd')
		
		self._add_vulnerability(extra_user)
		
		passwd2_vuln = self._new_vulnerability('USERGROUP_UNKNOWN_PASSWORD', 'Changes the password of users to unknown ones')
		passwd2_vuln.add_cmd_uses('passwd')
		
		self._add_vulnerability(passwd2_vuln)
		
		shell_vuln = self._new_vulnerability('USERGROUP_ADD_SHELLS', 'Changes shells of users')
		
		self._add_vulnerability(shell_vuln)
		
		
		admin_grp_vuln = self._new_vulnerability('USERGROUP_ADD_ADMIN_GROUP', 'Adds a user to an administrator group')
		
		self._add_vulnerability(admin_grp_vuln)
		
		wheel_vuln = self._new_vulnerability('USERGROUP_FAKE_ROOT', 'Creates a user with uid 0')
		wheel_vuln.add_cmd_uses('passwd')
		
		self._add_vulnerability(wheel_vuln)
		

	def name(self):
		return "User/Group Modification Module"
		
	def version(self):
		return "0.0.1"
		
	def author(self):
		return "Jacob Hartman" 

	def description(self):
		return "Misconfigures user and groups, such as adding new root users and setting weak passwords"

	def run(self):
		pass
		
	## Function for when a vulnerability is tested
	def test_run(self, vuln_obj, options={}):
		if vuln_obj.get_name() == 'USERGROUP_ADD_SHELLS':
			return self.__vuln_change_shells(options['user'], options['shell'])
		elif vuln_obj.get_name() == 'USERGROUP_ADD_ADMIN_GROUP':
			return self.__vuln_add_to_group(options['user'], 'root')
		elif vuln_obj.get_name() == 'USERGROUP_FAKE_ROOT':
			self.doc.add_doc("usergroup", 'USERGROUP_FAKE_ROOT', "Adding fake root user of " + options['user'])
			return self.__vuln_add_root_user(options['user'], options['password'])
		elif vuln_obj.get_name() == 'USERGROUP_WEAK_PASSWORD':
			return self.set_password(options['user'], options['password'])
		else:
			print("Vulnerability does not exist or cannot be tested")	
			
	def __vuln_change_shells(self, user, shell):
		passwd_file = self.file("/etc/passwd")
		result = passwd_file.regex_replace("^(" + user + ":.*):[^:]*$", "\\1:" + shell)
		if result == False:
			return False
		else:
			print(result)
			passwd_file.write_contents(result)
	
	def __vuln_add_to_group(self, user, group):
		
		check_list = self.get_group_list()
		print(check_list)
		
		if not group in check_list:
			print("Group does not exist")
			return False
		
		if user in check_list[group][1]:
			print("User is already in group")
			return True
		
		group_file = self.file("/etc/group")
		grp_file_content = group_file.get_contents()
		
		lines = grp_file_content.split("\n")
		
		for line in lines:
			line_list = line.split(":")
			
			if line_list[0].strip() == group:
				if line_list[3].strip() == "":
					result = group_file.regex_replace("^(" + group + ":.*)$", "\\1" + user)
				else:
					result = group_file.regex_replace("^(" + group + ":.*)$", "\\1," + user)
				
				if result == False:
					return False
				else:
					pass
					return group_file.write_contents(result)
	
	
	def __vuln_add_root_user(self, user, password):
		
		if not self.cross_version().isstring(user):
			print("User value is not a string")
			return False
		
		
		if user in self.get_user_list():
			print("User aleady exists")
			return False
		
		result = self.add_user(user, uid=0, gid=0, unique=False, shell="/bin/sh", makeusergroup=False)
		
		if result == False:
			print("Error adding user")
			return False

		return self.set_password(user, password)
		
		
	def set_password(self, user, password):
		if user == "root":
			user = ""
		
		set_password = self.command()
		(returncode, output_list, error_list) = set_password.run("passwd " + user, [password , password])
		
		if len(error_list) > 0:
			if not 'password updated successfully' in error_list[0]:
				print("Error running passwd")
				print(error_list)
				return False
			else:
				return True
		return True
		
	def get_group_list(self):
		group_file = self.file("/etc/group")
		grp_file_content = group_file.get_contents()
		
		group_list = {}
		lines = grp_file_content.split("\n")
	
		for line in lines:
			
			if line.strip() == "":
				continue
			
			split_line = line.split(":")
			
			
			grp_name = split_line[0].strip()
			grp_id = split_line[2].strip()
			members = split_line[3].strip().split(",")
			
			group_list[grp_name] = (grp_id, members)
		
		return group_list
			
	def get_user_list(self):
		passwd_file = self.file("/etc/passwd")
		
		passwd_content = passwd_file.get_contents()
		passwd_lines = passwd_content.split("\n")
		
		user_list = {}
		
		for line in passwd_lines:
			
			split_line = line.split(":")
			
			if len(split_line) == 7 and split_line[2].isdigit():
				username = split_line[0]
				uid = int(split_line[2])
				user_list[username] = (uid, split_line[6])
			else:
				pass
				
		return user_list
	
	
	def add_user(self, username, uid="", gid="" ,homedir="", makehomedir=True, groups=[], unique=True, system=False, makeusergroup=True, shell=""):
		command_string = "useradd"
		
		if isinstance( uid, int ) or uid.isdigit():
			command_string += " -u " + str(uid)
		else:
			raise ValueError("UID must be an integer")
		
		if isinstance( gid, int ) or gid.isdigit():
			command_string += " -g " + str(gid)
		elif gid == "":
			pass
		else:
			raise ValueError("UID must be an integer")
		
		if homedir != "":
			command_string += " -d " + str(homedir)
		
		if makehomedir == True:
			command_string += " -m" 
		elif makehomedir == False:
			command_string += " -M"
		else:
			raise ValueError("Invalid makehomedir value")
		
		if len(groups) > 0:
			command_string += " -G "
			for i in range(len(groups)):
				if i == 0:
					command_string += str(groups[i])
				else:
					command_string += "," + str(groups[i])
		
		if unique == False:
			command_string += " -o"
		
		if system == True:
			command_string += " -r"
		
		if makeusergroup == True:
			command_string += " -U"
		elif makeusergroup == False:
			command_string += " -N"
		else:
			raise ValueError("Invalid makeusergroup value")
			
		if shell != "":
			test = self.file(shell)
			if test.exists():
				command_string += " -s " + shell
			else:
				raise ValueError("Shell " + str(shell) + "could not be found")
				
		command_string += " " + username
		
		add_command = self.command()
		
		(returncode, output_list, error_list) = add_command.run(command_string)
		
		if len(error_list) > 0:
			print(error_list)
			return False
		else:
			return True

