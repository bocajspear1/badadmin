## @package util.simple_filesystem
#
# Provides simplified access to accessing and modifiying files on the system
#
import shutil
import os
import util.cross_version 
import pwd
import grp
import re


class simple_file():
	
	## Constructor
	#
	# @param string filename - The name of the file
	#	
	def __init__(self, filename):
		if filename.strip() != "":
			# Test to see if the path is not a directory
			if os.path.isdir(filename):
				raise ValueError("Directory exists at this location")
			else:
				self.file = filename
		else:
			raise ValueError("File cannot be blank")
	
	## Creates the file. 
	#
	# @param boolean clobber - True if the file is clobbered, False (default)
	# if not
	# @returns boolean - True if successful, False if not
	#
	def create(self, clobber=False):

		if not self.exists() or (self.exists() and clobber == True):
			try:
				if self.file != None:
					with open(self.file, 'w+') as content_file:
						return True
				else:
					return False
			except IOError:
				print ("Error creating file")
				return False
		else:
			return False
	
	## Deletes the file. 
	#
	# @returns boolean - True if successful, False if not
	#
	def remove(self):
		try:
			if self.file != None:
				os.remove(self.file)
				return True
		except IOError:
			print ("Could not find selected file")
			return False
		except OSError:
			print ("Could not find selected file")
			return False
	
	## Returns the raw contents of the file
	#
	# @returns string|boolean - String contents if successful, False if not
	#
	def get_contents(self):
		try:
			if self.file != None:
				content = ""
				with open(self.file, 'r') as content_file:
					content = content_file.read()
				return content	
		except IOError:
			print ("Could not find selected file")
			return False
	
	## Writes to the file, clobbering anything already there
	# REPEAT: DELETES ANYTHING ALREADY THERE!
	#
	# @param string contents - Data to write to file
	# @returns boolean - True if successful, False if not
	#
	def write_contents(self, contents):
		try:
			if self.file != None:
				with open(self.file, 'w+') as content_file:
					content_file.write(contents)
					return True
		except IOError:
			print ("Could not write to selected file")
			return False
	
	## Moves file to the given location
	#
	# @param string to_location - Location to move the file to
	# @returns boolean - True if successful, False if not
	#
	def move(self, to_location):
		try:
			shutil.move(self.file, to_location)
			return True
		except shutil.Error:
			print("ERROR - Could not copy file")
			return False
	
	## Copies file to given location. Can keep all meta-data and permissions, or not
	#
	# @param string to_location - Location to move the file to
	# @param boolean keep - True keeps all metadata and permissions, False does not
	# @returns boolean - True if successful, False if not
	#
	def copy(self, to_location, keep=False):
		try:
			if keep == False:
				shutil.copyfile(self.file, to_location)
				return True
			elif keep == True:
				shutil.copy2(self.file, to_location)
				return True
			else:
				print("Invalid keep value")
				return False
		except shutil.Error:
			print("ERROR - Could not copy file")
			return False
	
	## Does a line by line replace in the file
	#
	# @param string search - The string value to search for
	# @param string replace - The value to replace the search with
	# @returns string|boolean - The new contents, False if an error
	#
	def replace(self, search, replace):
		if self.exists():
			file_contents = self.get_contents()
			
			if not file_contents == False:
			
				file_lines = file_contents.split("\n")
				
				for i in range(len(file_lines)):
					file_lines[i] =file_lines[i].replace(search, replace)
				
				new_contents = "\n".join(file_lines)
				
				return new_contents
			else:
				return False
		else:
			return False
	
	## Does a line by line regex replace in the file
	#
	# @param string search - The regex value to search for
	# @param string replace - The value to replace the search with
	# @returns string|boolean - The new contents, or False if failed
	#
	def regex_replace(self, search, replace):
		if self.exists():
			file_contents = self.get_contents()
			
			if not file_contents == False:
				file_lines = file_contents.split("\n")
				
				re_search = re.compile(search)
				
				for i in range(len(file_lines)):
					file_lines[i] = re.sub(re_search, replace, file_lines[i])
				
				new_contents = "\n".join(file_lines)
				
				return new_contents
				
			else:
				return False
		else:
			return False
	
	## Writes the content to the end of the file
	#
	# @param string content - The content to append to the file
	# @returns boolean - True if successful, False if not
	def append_content(self, content):
		try:
			if self.file != None:
				with open(self.file, 'a') as content_file:
					content_file.write(content)
					return True
		except IOError:
			print ("Could not find selected file")
			return False

		
	def append_file_to(self, content, append_to):
		pass
	
	
	
	## Checks if the file actually exists in the filesystem
	#
	# @param string content - The content to append to the file
	# @returns boolean- True if successful, False if not
	def exists(self):
		return os.path.isfile(self.file)
	
	
	## Set the permissions for the file
	#
	# @param integer owner - Permission flag for the owner (0-7)
	# @param integer group - Permission flag for the group (0-7)
	# @param integer other - Permission flag for other (0-7)
	# @param integer special - Special file flags, such as setuid and sticky (0-7)
	# @returns boolean - True if successful, False if not	
	def set_permissions(self, owner, group, other, special=0):
		if (owner >= 0 and owner <= 7) and (group >= 0 and group <= 7) and (other >= 0 and other <= 7) and (special >= 0 and special <= 7):
			permission_string = str(special)  + str(owner)  + str(group)  + str(other)
			try:
				os.chmod(self.file, int(permission_string, 8))
				return True
			except:
				print("Could not set permissions for file")
				return False
		else:
			print("Invalid permission flag")
			return False
			
	## Gets the permissions for the file
	#
	# @returns dict|boolean - A dict containing the permissions by name, False if not. Dict contains the following:
	#  * owner - The permission flag for the owner	
	#  * group - The permission flag for the group	
	#  * other - The permission flag for other	
	#  * special - The special permissions flag
	def get_permissions(self):
		try:
			stat_result = self.get_stat()
			
			if not stat_result == False:
				permission_string  = oct(stat_result.st_mode)[-4:]
				
				file_permissions = {"owner": int(permission_string[1:2]), 
				"group": int(permission_string[2:3]),
				"other": int(permission_string[3:4]),			
				"special": int(permission_string[0:1])}

				return file_permissions
				
			else:
				return False
				
		except: 
			return False
	
	## Set the ownership of the file by uid and guid
	#
	# @param integer uid - The uid of the new owner
	# @param integer gid - The gid of the new owning group
	# @returns boolean - True if successful, False if not	
	#
	def set_ownership_by_id(self, uid, gid):
		try:
			os.chown(self.file, uid, gid)
			return True
		except:
			print("Could not change the file's permissions")
			return False

	## Set the ownership of the file by name of the user and group
	#
	# @param integer u_name - The name of the new owner
	# @param integer g_name - The name of the new owning group
	# @returns boolean - True if successful, False if not	
	#
	def set_ownership_by_name(self, u_name, g_name):
		try:
			uid = pwd.getpwnam(u_name)
			gid = grp.getgrnam(g_name)
			
			return self.set_ownership_by_id(uid[2], gid[2])
			
		except KeyError:
			
			print("Could not find user or group")
			return False
	
	## Gets the ownership of the file
	#
	# @returns dict - An dict containing the following information:
	#  * uid - UID
	#  * gid - GID
	#  * owner_name - Username of the owning user
	#  * group_name - Name of the owning group
	#	
	def get_ownership(self):
		stat_result = self.get_stat()
		
		if not stat_result == None:
			file_uid = stat_result.st_uid
			file_gid = stat_result.st_gid
			
			file_owner_name = pwd.getpwuid(file_uid).pw_name
			file_group_name = grp.getgrgid(file_gid).gr_name
			
			return {"uid": file_uid, "owner_name": file_owner_name, "gid": file_gid, "group_name": file_group_name}
			
		else:
			return False
	
	## Gets the stat output for the file
	#
	# @returns tuple|boolean - os.stat tuple, or False if failed
	#
	def get_stat(self):
		try:
			stat_result = os.stat(self.file)
			return stat_result
		except:
			print("Failed to get stat for file")
			return None
			
## Provides simplified access to using and modifing directories
#	
class simple_dir():
	## Constructor
	#
	# @param string dirname - The name of the directory
	#	
	def __init__(self, dirname):
		if dirname.strip() != "":
			if os.path.isfile(dirname):
				raise ValueError("File already at the location")
			else:
				self.dir = dirname
		else:
			raise ValueError("Directory cannot be blank")

	## List the contents of the directory
	#
	# @returns string[]|boolean - List of results if successful, False if not
	#
	def list(self):
		try:
			return os.listdir(self.dir)
		except:

			print("Could not list the contents of the directory")
			return False
	
	## Attempts to creates the directory
	#
	# @returns boolean - True if successful, False if not
	#
	def create(self):
		try:
			os.mkdir(self.dir)
			return True
		except  OSError as e:
			#~ print(e.strerror)
			print("Failed to create directory")
			return False
	
	## Attempts to remove the directory
	#
	# @returns boolean - True if successful, False if not
	#
	def remove(self):
		try:
			shutil.rmtree(self.dir)
			return True
		except:
			print("Could not remove directory")
			return False
	
	## Copies the directory to the given location
	#
	# @param string to_location - Location to copy the directory to
	# @returns boolean - True if successful, False if not
	#		
	def copy(self, to_location):
		try:
			shutil.copytree(self.dir, to_location)
			return True
		except:
			print("Could not copy directory")
			return False
	
	## Moves the directory to the given location
	#
	# @param string to_location - Location to move the directory to
	# @returns boolean - True if successful, False if not
	#		
	def move(self, to_location):
		try:
			shutil.move(self.dir, to_location)
			return True
		except:
			print("Could not move directory")
			return False
	
	## Checks if the directory actually exists on the filesystem
	#
	# @returns boolean - True if it does, False if not
	#		
	def exists(self):
		return os.path.isdir(self.dir)
	
	
	def set_permissions(self, owner, group, other, flag=0):
		if (owner >= 0 and owner <= 7) and (group >= 0 and group <= 7) and (other >= 0 and other <= 7) and (flag >= 0 and flag <= 7):
			permission_string =  str(flag)  + str(owner)  + str(group)  + str(other)
			try:
				os.chmod(self.dir, int(permission_string, 8))
				return True
			except:
				print("Could not set permissions for file")
				return False
			
	def get_permissions(self):
		try:
			stat_result = self.get_stat()
			
			if not stat_result == False:
				permission_string  = oct(stat_result.st_mode)[-4:]
				
				dir_permissions = {"owner": int(permission_string[1:2]), 
				"group": int(permission_string[2:3]),
				"other": int(permission_string[3:4]),			
				"special": int(permission_string[0:1])}

				return dir_permissions
				
			else:
				return False
				
		except: 
			return False
		
	
	
	def set_ownership_by_id(self, uid, gid):
		try:
			os.chown(self.dir, uid, gid)
			return True
		except:
			print("Could not change the directory's owner")
			return False
	
	def set_ownership_by_name(self, u_name, g_name):
		try:
			uid = pwd.getpwnam(u_name)
			gid = grp.getgrnam(g_name)
		except:
			print("Could not find user or group")
			return False
			
		return self.set_ownership_by_id(uid, gid)
	
	def get_ownership(self):
		stat_result = self.get_stat()
		
		if not stat_result == False:
			dir_uid = stat_result.st_uid
			dir_gid = stat_result.st_gid
			
			dir_owner_name = pwd.getpwuid(dir_uid).pw_name
			dir_group_name = grp.getgrgid(dir_gid).gr_name
			
			return {"uid": dir_uid, "owner_name": dir_owner_name, "gid": dir_gid, "group_name": dir_group_name}
			
		else:
			return False
	
	def get_stat(self):
		return os.stat(self.dir)
	
	def recursive_chmod(self, owner, group, other, flag=0):
		for subdir, dirs, files in os.walk(self.dir):

			tmp_dir = simple_dir(subdir)
			result = tmp_dir.set_permissions(owner, group, other, flag)
			if result == False:
				return False
				
			for file in files:
				file_path = os.path.join(subdir, file)
				
				tmp_file = simple_file(file_path)
				result = tmp_file.set_permissions(owner, group, other, flag)
				if result == False:
					return False
		return True
		
	def recursive_chown_by_id(self, uid, gid):
		for subdir, dirs, files in os.walk(self.dir):

			tmp_dir = simple_dir(subdir)
			result = tmp_dir.set_ownership_by_id(uid, gid)
			if result == False:
				return False
				
			for file in files:
				file_path = os.path.join(subdir, file)
				
				tmp_file = simple_file(file_path)
				result = tmp_file.set_ownership_by_id(uid, gid)
				if result == False:
					return False
		return True
	
	def recursive_chown_by_name(self, u_name, g_name):
		try:
			uid = pwd.getpwnam(u_name)
			gid = grp.getgrnam(g_name)
		except KeyError:
			print("Could not find user or group")
			return False
			
		return self.recursive_chown_by_id(uid[2], gid[2])


