# Import the base module
from ..base import module_base

class nfs_config(module_base):
	
	def __init__(self):
		super(nfs_config, self).__init__()
		
		root_export_vuln = self._new_vulnerability('UNSECURE_EXPORT_ROOT_FS', 'Exports the entire root fs with very low security')
		root_export_vuln.add_dependency('nfsserver', '*')
		root_export_vuln.set_difficulty('easy')
		self._add_vulnerability(root_export_vuln)
		
		low_sec_vuln = self._new_vulnerability('LOW_SECURITY_EXPORT', 'Adds an export that has low security')
		low_sec_vuln.add_dependency('nfsserver', '*')
		low_sec_vuln.set_difficulty('medium')
		self._add_vulnerability(low_sec_vuln)
		
		
		none_vuln = self._new_vulnerability('NONE', 'Creates a normal NFS share')
		none_vuln.add_dependency('nfsserver', '*')
		self._add_vulnerability(none_vuln)
		

	def name(self):
		return "NFS Configuration Module"
		
	def version(self):
		return "0.0.1"
		
	def author(self):
		return "Jacob Hartman" 

	def description(self):
		return "Sets possibly insecure NFS configurations"

	def run(self):
		pass
		
	## Function for when a vulnerability is tested
	def test_run(self, vuln_obj, options={}):
		if vuln_obj.get_name() == 'UNSECURE_EXPORT_ROOT_FS':
			return self.__vuln_root_fs()
		elif vuln_obj.get_name() == 'LOW_SECURITY_EXPORT':
			pass
		else:
			print("Vulnerability does not exist or cannot be tested")	
	
	def __get_exports_file(self):
		exports_file = self.file("/etc/exports")
		
		if not exports_file.exists():
			exports_file.create()
		
		return exports_file
		
	def __vuln_root_fs(self):
		
		exports_file = self.__get_exports_file()
		
		options = "no_root_squash"

		line = "/ *(" + options + ")\n"
		
		file_status = exports_file.append_content(line)

		if file_status == False:
			print("Error appending to exports file")
			return False
		
		command_status = self.command().run("exportfs -ra")

		if command_status == False:
			print("Error refreshing exports")
			return False

		return True
