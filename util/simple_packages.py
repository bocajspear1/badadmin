## @package util.simple_packages
#
# Simplified interactions with the system package manager
#
import util.cross_version as cross_version
import util.version_util as version_util
import util.simple_command as simple_command
from util.simple_filesystem import simple_file
from util.simple_filesystem import simple_dir
import subprocess

## Simplified package management
#
class simple_packages:
	
	## Create a new instance of simple_packages
	def __init__(self):
		self.__package_manager = None
		self.__detect_package_manager()
		if self.__package_manager == None:
			print("Package manager on the system is not supported")
			
	# Detect what package manager is installed
	def __detect_package_manager(self):
		pkg_manager_list = [
		'yum',
		'apt-get'
		]
		
		if simple_file("/etc/yum.conf").exists():
			self.__package_manager = "yum"
		elif simple_dir("/etc/apt").exists():
			self.__package_manager = "apt"
			
	## Get the package manager on the system
	# 
	# @returns string - The name of the package manager
	#
	def get_package_manager(self):
		return self.__package_manager
	
	## Check if the package is installed
	#
	# @param package (string) - The name of the package to check
	# @returns bool - True if the package is installed, False if not
	#
	def is_installed(self, package):
		
		if not cross_version.isstring(package):
			raise ValueError("Package name is not a string")
		
		exists_command = ""
		
		if self.__package_manager == "yum":
			exists_command = "yum list installed " + package
		elif self.__package_manager == "apt":
			exists_command = "dpkg -s " + package
		
		returncode, return_list, error_list = simple_command.simple_command().run(exists_command)
		
		if self.__package_manager == "yum":
			if returncode == 0:
				return True
			else:
				return False
		elif self.__package_manager == "apt":
			if returncode == 0:
				return True
			else:
				return False
	
	## Install a package to the system
	#
	# @param package (string) - The name of the package to install
	# @param version (string) - The version of the package to install. Defaults to None which installs the latest version
	#
	def install(self, package, version=None):
		
		if not cross_version.isstring(package):
			raise ValueError("Package name is not a string")
		
		install_command = ""
		
		if self.__package_manager == "yum":
			install_command = "yum install -y " + package
		elif self.__package_manager == "apt":
			returncode, return_list, error_list = simple_command.simple_command().run("apt-get update")
			install_command = "apt-get install -y " + package
		
		returncode, return_list, error_list = simple_command.simple_command().run(install_command)
		
		if returncode == 0:
			return True
		else:
			return False
	
	## Removes a package from the system
	#
	# @param package (string) - Name of the package to remove
	# @returns bool - True if successful, False if not
	#
	def remove(self, package):
		return self.uninstall(package)
	
	## Removes a package from the system
	#
	# @param package (string) - Name of the package to remove
	# @returns bool - True if successful, False if not
	#
	def uninstall(self, package):	
		if not cross_version.isstring(package):
			raise ValueError("Package name is not a string")
		
		uninstall_command = ""
		
		if self.__package_manager == "yum":
			install_command = "yum remove -y " + package
		elif self.__package_manager == "apt":
			install_command = "apt-get remove -y --purge " + package
		
		returncode, return_list, error_list = simple_command.simple_command().run(install_command)

		if returncode == 0:
			return True
		else:
			return False
		
	def available_versions(self, package):
		pass

