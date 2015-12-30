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

## Base class for files and directories that contains common functions that work for both
#
class simple_fs_item(object):
	
	## Note: Don't directly create this object
	def __init__(self, path):
		self.__path = path
	
	## Gets the stat output for the file
	#
	# @returns tuple|None - os.stat tuple, or None if failed
	#
	def get_stat(self):
		try:
			stat_result = os.stat(self.__path)
			return stat_result
		except:
			print("Failed to get stat for file")
			return None
	
	## Set the permissions for the file
	#
	# @param owner (int) - Permission flag for the owner (0-7)
	# @param group (int) - Permission flag for the group (0-7)
	# @param other (int) - Permission flag for other (0-7)
	# @param special (int) - Special file flags, such as setuid and sticky (0-7)
	# @returns bool - True if successful, False if not	
	#
	def set_permissions(self, owner, group, other, special=0):
		if (owner >= 0 and owner <= 7) and (group >= 0 and group <= 7) and (other >= 0 and other <= 7) and (special >= 0 and special <= 7):
			permission_string = str(special)  + str(owner)  + str(group)  + str(other)
			try:
				os.chmod(self.__path, int(permission_string, 8))
				return True
			except:
				print("Could not set permissions for file")
				return False
		else:
			print("Invalid permission flag")
			return False	
	
	## Gets the permissions for the file
	#
	# @returns dict|None - A dict containing the permissions by name, None if not. Dict contains the following:
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
				return None
				
		except: 
			return None
	
	## Set the ownership of the file by uid and guid
	#
	# @param uid (int|None) - The uid of the new owner, None if no changes are to be made
	# @param gid (int|None) - The gid of the new owning group, None if no changes are to be made
	# @returns bool - True if successful, False if not	
	#
	def set_ownership_by_id(self, uid=None, gid=None):
		
		if uid == None:
			uid = -1
		if gid == None:
			gid = -1
		
		try:
			os.chown(self.__path, uid, gid)
			return True
		except:
			print("Could not change the file's permissions")
			return False
	
	## Set the ownership of the file by name of the user and group
	#
	# @param u_name (string|None) - The name of the new owner, None if no changes are to be made
	# @param g_name (string|None) - The name of the new owning group, None if no changes are to be made
	# @returns bool - True if successful, False if not	
	#
	def set_ownership_by_name(self, u_name=None, g_name=None):
		try:
			if not u_name == None:
				uid = pwd.getpwnam(u_name).pw_uid
			else:
				uid = None
				
			if not g_name == None:
				gid = grp.getgrnam(g_name).gr_gid
			else:
				gid = None
			
			return self.set_ownership_by_id(uid, gid)
			
		except KeyError:
			print("Could not find user or group")
			return False
	
	## Gets the ownership of the file
	#
	# @returns dict|None - An dict containing the following information:
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
			return None
	
	## Moves the directory to the given location
	#
	# @param to_location (string) - Location to move the directory to
	# @returns bool - True if successful, False if not
	#		
	def move(self, to_location):
		try:
			shutil.move(self.__path, to_location)
			return True
		except:
			print("Could not move directory")
			return False
	
class simple_file(simple_fs_item):
	
	## Constructor
	#
	# @param filename (string) - The name of the file
	#	
	def __init__(self, filename):
		super(simple_file, self).__init__(filename)
		if filename.strip() != "":
			# Test to see if the path is not a directory
			if os.path.isdir(filename):
				raise ValueError("Directory exists at this location")
			else:
				self.__file = filename
		else:
			raise ValueError("File cannot be blank")
	
	## Creates the file. 
	#
	# @param clobber (bool) - True if the file is clobbered, False (default)
	# if not
	# @returns bool - True if successful, False if not
	#
	def create(self, clobber=False):

		if not self.exists() or (self.exists() and clobber == True):
			try:
				if self.__file != None:
					with open(self.__file, 'w+') as content_file:
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
	# @returns bool - True if successful, False if not
	#
	def remove(self):
		try:
			if self.__file != None:
				os.remove(self.__file)
				return True
		except IOError:
			print ("Could not find selected file")
			return False
		except OSError:
			print ("Could not find selected file")
			return False
	
	## Returns the raw contents of the file
	#
	# @returns string|None - String contents if successful, None if not
	#
	def get_contents(self):
		try:
			if self.__file != None:
				content = ""
				with open(self.__file, 'r') as content_file:
					content = content_file.read()
				return content	
		except IOError:
			print ("Could not find selected file")
			return None
	
	## Writes to the file, clobbering anything already there
	# REPEAT: DELETES ANYTHING ALREADY THERE!
	#
	# @param contents (string) - Data to write to file
	# @returns bool - True if successful, False if not
	#
	def write_contents(self, contents):
		try:
			if self.__file != None:
				with open(self.__file, 'w+') as content_file:
					content_file.write(contents)
					return True
		except IOError:
			print ("Could not write to selected file")
			return False
	
	## Copies file to given location. Can keep all meta-data and permissions, or not
	#
	# @param to_location (string) - Location to move the file to
	# @param keep (bool) - True keeps all metadata and permissions, False does not
	# @returns bool - True if successful, False if not
	#
	def copy(self, to_location, keep=False):
		try:
			if keep == False:
				shutil.copyfile(self.__file, to_location)
				return True
			elif keep == True:
				shutil.copy2(self.__file, to_location)
				return True
			else:
				print("Invalid keep value")
				return False
		except shutil.Error:
			print("ERROR - Could not copy file")
			return False
	
	## Does a line by line replace in the file
	#
	# @param search (string) - The string value to search for
	# @param replace (string) - The value to replace the search with
	# @returns string|bool - The new contents, False if an error
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
	# @param search (string) - The regex value to search for
	# @param replace (string) - The value to replace the search with
	# @returns string|bool - The new contents, or False if failed
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
	# @param content (string) - The content to append to the file
	# @returns bool - True if successful, False if not
	#
	def append_content(self, content):
		try:
			if self.__file != None:
				with open(self.__file, 'a') as content_file:
					content_file.write(content)
					return True
		except IOError:
			print ("Could not find selected file")
			return False
	
	def append_file_to(self, content, append_to):
		pass
	
	## Checks if the file actually exists in the filesystem
	#
	# @returns bool- True if the file exists False if not
	#
	def exists(self):
		return os.path.isfile(self.__file)
	
			
## Provides simplified access to using and modifing directories
#	
class simple_dir(simple_fs_item):
	## Constructor
	#
	# @param dirname (string) - The name of the directory
	#  
	def __init__(self, dirname):
		super(simple_dir, self).__init__(dirname)
		if dirname.strip() != "":
			if os.path.isfile(dirname):
				raise ValueError("File already at the location")
			else:
				self.__dir = dirname
		else:
			raise ValueError("Directory cannot be blank")

	## List the contents of the directory
	#
	# @returns string[]|bool - List of results if successful, None if not
	#
	def list(self):
		try:
			return os.listdir(self.__dir)
		except:

			print("Could not list the contents of the directory")
			return None
	
	## Attempts to creates the directory
	#
	# @returns bool - True if successful, False if not
	#
	def create(self):
		try:
			os.mkdir(self.__dir)
			return True
		except  OSError as e:
			#~ print(e.strerror)
			print("Failed to create directory")
			return False
	
	## Attempts to remove the directory
	#
	# @returns bool - True if successful, False if not
	#
	def remove(self):
		try:
			shutil.rmtree(self.__dir)
			return True
		except:
			print("Could not remove directory")
			return False
	
	## Copies the directory to the given location
	#
	# @param to_location (string) - Location to copy the directory to
	# @returns bool - True if successful, False if not
	#		
	def copy(self, to_location):
		try:
			shutil.copytree(self.__dir, to_location)
			return True
		except:
			print("Could not copy directory")
			return False
	
	
	
	## Checks if the directory actually exists on the filesystem
	#
	# @returns bool - True if it does, False if not
	#		
	def exists(self):
		return os.path.isdir(self.__dir)
	
	## Recusively sets the permissions for all items within the directory
	#
	# @param owner (int) - Permission flag for the owner (0-7)
	# @param group (int) - Permission flag for the group (0-7)
	# @param other (int) - Permission flag for other (0-7)
	# @param special (int) - Special file flags, such as setuid and sticky (0-7)
	# @returns bool - True if successful, False if not
	#
	def recursive_chmod(self, owner, group, other, flag=0):
		for subdir, dirs, files in os.walk(self.__dir):

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
	
	##  Recusively sets the ownership for all items within the directory, set by id
	#
	# @param uid (int|None) - The uid of the new owner, None if no changes are to be made
	# @param gid (int|None) - The gid of the new owning group, None if no changes are to be made
	# @returns bool - True if successful, False if not	
	#
	def recursive_chown_by_id(self, uid=None, gid=None):
		for subdir, dirs, files in os.walk(self.__dir):

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
	
	## Recusively sets the ownership for all items within the directory, set by name
	#
	# @param u_name (string|None) - The name of the new owner, None if no changes are to be made
	# @param g_name (string|None) - The name of the new owning group, None if no changes are to be made
	# @returns bool - True if successful, False if not	
	#
	def recursive_chown_by_name(self, u_name=None, g_name=None):
		try:
			uid = pwd.getpwnam(u_name)
			gid = grp.getgrnam(g_name)
		except KeyError:
			print("Could not find user or group")
			return False
			
		return self.recursive_chown_by_id(uid[2], gid[2])


