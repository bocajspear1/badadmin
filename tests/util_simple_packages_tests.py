from util.simple_packages import simple_packages
import util.os_data as os_data

def test_get_package_manager():
	test = simple_packages()
	my_os = os_data.os_info()
	
	ubuntu_match = os_data.os_match('linux', 'ubuntu')
	centos_match = os_data.os_match('linux', 'centos')
	
	if my_os.matches(ubuntu_match):
		assert test.get_package_manager() == "apt"
	elif my_os.matches(centos_match):
		assert test.get_package_manager() == "yum"

#~ def test_install():
	#~ test = simple_packages()
	#~ my_os = os_data.os_info()
	
	#~ ubuntu_match = os_data.os_match('linux', 'ubuntu')
	#~ centos_match = os_data.os_match('linux', 'centos')
	
	
	
	#~ if my_os.matches(ubuntu_match):
		#~ package = 'apache2'
	#~ elif my_os.matches(centos_match):
		#~ package = 'httpd'
		
	#~ assert test.is_installed(package) == False
	
	#~ assert test.install(package) == True
	
	#~ assert test.is_installed(package) == True
	
	#~ assert test.remove(package) == True
