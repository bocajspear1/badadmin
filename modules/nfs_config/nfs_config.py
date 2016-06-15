# Import the base module
from ..base import module_base

UNSAFE_SHARES = [
	"/var/www",
	"/tmp/share",
	'/etc',
	'/var'
]

SAFE_SHARES = [
	"/var/nfsshare",
	"/var/nfs/",
	"/tmp/tmpshare"
]

class nfs_config(module_base):
	
	def __init__(self):
		super(nfs_config, self).__init__()
		
		root_export_vuln = self.new_vulnerability('UNSECURE_EXPORT_ROOT_FS', 'Exports the entire root fs with very low security')
		root_export_vuln.add_dependency(('nfsserver', '*'))
		root_export_vuln.set_difficulty('easy')
		self.add_vulnerability(root_export_vuln)
		
		low_sec_vuln = self.new_vulnerability('LOW_SECURITY_EXPORT', 'Adds an export that has low security')
		low_sec_vuln.add_dependency(('nfsserver', '*'))
		low_sec_vuln.set_difficulty('medium')
		self.add_vulnerability(low_sec_vuln)
		
		
		none_vuln = self.new_vulnerability('NONE', 'Creates a normal NFS share')
		none_vuln.add_dependency(('nfsserver', '*'))
		self.add_vulnerability(none_vuln)
		

	def name(self):
		return "NFS Configuration Module"
		
	def version(self):
		return "0.0.1"
		
	def author(self):
		return "Jacob Hartman" 

	def description(self):
		return "Sets possibly insecure NFS configurations"

	def run(self):
		status = True
		
		for vuln in self.get_running_vulns():
			if vuln.name() == 'UNSECURE_EXPORT_ROOT_FS':
				result = self.__vuln_root_fs()
				if result == True:
					self.doc.add_doc("UNSECURE_EXPORT_ROOT_FS", "Exporting entire root filesystem with no root_squashing (allows remote mounting as root)")
				status = status and result
			elif vuln.name() == 'LOW_SECURITY_EXPORT':
				export_loc = self.random().array_random(UNSAFE_SHARES)
				export_dir = self.dir(export_loc)
				if not export_dir.exists():
					result = export_dir.create()
					if result == False:
						status = False
				
				result = self.__add_export(export_loc, "*", "no_root_squash,rw")
				if result == True:
					self.doc.add_doc("LOW_SECURITY_EXPORT", "Exporting " + export_loc + " with low security")
				status = status and result
				
			elif vuln.name() == 'NONE':
				export_loc = self.random().array_random(SAFE_SHARES)
				export_dir = self.dir(export_loc)
				if not export_dir.exists():
					result = export_dir.create()
					if result == False:
						status = False
				
				result = self.__add_export(export_loc, "*", "all_squash,ro")
				if result == True:
					self.doc.add_doc("NONE", "Exporting " + export_loc + " with improved security")
				status = status and result
			else:
				print("Invalid vulnerability")
				status = False
			
			
			
		return status
		
		
	## Function for when a vulnerability is tested
	def test_run(self, vuln_obj, options={}):
		if vuln_obj.name() == 'UNSECURE_EXPORT_ROOT_FS':
			return self.__vuln_root_fs()
		elif vuln_obj.name() == 'LOW_SECURITY_EXPORT':
			pass
		else:
			print("Vulnerability does not exist or cannot be tested")	
	
	def __get_exports_file(self):
		exports_file = self.file("/etc/exports")
		
		if not exports_file.exists():
			exports_file.create()
		
		return exports_file
	
	def __add_export(self, path, network ,options):
		exports_file = self.__get_exports_file()
		line = path + " " + network + "(" + options + ")\n"
		file_status = exports_file.append_content(line)
		
		if file_status == False:
			print("Error appending to exports file")
			return False
		
		command_status = self.command().run("exportfs -ra")

		if command_status == False:
			print("Error refreshing exports")
			return False
		
		return True
		
	def __vuln_root_fs(self):
		

		options = "no_root_squash,insecure,rw"
		result = self.__add_export("/", "*", options)
		
		
		return result
