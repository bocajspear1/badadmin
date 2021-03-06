# Import the base module
from ..base import module_base

class nfs_server(module_base):
	
	def __init__(self):
		super(nfs_server, self).__init__()
		
		none_vuln = self.new_vulnerability('NONE', 'Just installs the latest NFS server', 'nfsserver')
		none_vuln.add_supported_os('linux', 'ubuntu')
		none_vuln.add_supported_os('linux', 'centos', '<7')
		self.add_vulnerability(none_vuln)
		
	def name(self):
		return "NFS Server Module"
		
	def version(self):
		return "0.0.1"
		
	def author(self):
		return "Jacob Hartman" 

	def description(self):
		return "Installs an NFS server"

	def run(self):
		status = True
		
		for vuln in self.get_running_vulns():
			if vuln.name() == 'NONE':
				result = self.__vuln_none()
				if result == True:
					self.doc.add_doc("NONE", "Installed latest NFS server version")
				status = status and result
			else:
				print("Invalid vulnerability")
				status = False
				
	## Function for when a vulnerability is tested
	def test_run(self, vuln_obj, options={}):
		if vuln_obj.name() == 'NONE':
			return self.__vuln_none()
		else:
			print("Vulnerability does not exist or cannot be tested")	
			
	def __vuln_none(self):
		package = None
		
		if self.os_matches('linux', 'ubuntu'):
			package = "nfs-kernel-server"
		elif self.os_matches('linux', 'centos', '<7'):
			package = 'nfs-utils nfs-utils-lib'
		else:
			return False
			
		pm = self.package_manager()
		
		pm.install(package)
		
		return self.__post_install()
		
	def __post_install(self):
		
		cmd = self.command()
		total_codes = 0
		
		if self.os_matches('linux', 'ubuntu'):
			
			
			
			code, output, errors = cmd.run("service nfs-kernel-server start")
			total_codes += code
			
			if total_codes > 0:
				return False
				
		elif self.os_matches('linux', 'centos', '<7'):
			
			code, output, errors = cmd.run("chkconfig nfs on")
			total_codes += code
			code, output, errors = cmd.run("service rpcbind start")
			total_codes += code
			code, output, errors = cmd.run("service nfs start")
			total_codes += code
			
			if total_codes > 0:
				return False
		
		return True


