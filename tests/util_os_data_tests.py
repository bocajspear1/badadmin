# This unit tests the functionality of the util.os_data module
import util.os_data as os_data
import platform



def test_os_info_obj():

	data = os_data.os_info()

	if platform.system() == 'Linux':
		assert data.os_type() == 'linux'

		plat_data = platform.linux_distribution()
		
		if 'ubuntu' in plat_data[0].lower():
			assert data.flavor() == 'ubuntu'
			assert data.version() == plat_data[1]
		elif 'centos' in plat_data[0].lower():
			assert data.flavor() == 'centos'
			assert data.version() == plat_data[1]

def test_os_match_obj():
	test_obj = os_data.os_match('linux')
	assert test_obj.os_type() == "linux"
	assert test_obj.flavor() == "*"
	assert test_obj.version_range() == "*"
	
	test_obj = os_data.os_match('linux', 'ubuntu')
	assert test_obj.os_type() == "linux"
	assert test_obj.flavor() == 'ubuntu'
	assert test_obj.version_range() == "*"
	
	test_obj = os_data.os_match('linux', 'ubuntu', '>12.04')
	assert test_obj.os_type() == "linux"
	assert test_obj.flavor() == 'ubuntu'
	assert test_obj.version_range() == '>12.04'

def test_os_match_obj_invalid():
	try:
		invalid = os_data.os_match('nope')
	except ValueError:
		assert True

	try:
		invalid = os_data.os_match('linux', "nope")
	except ValueError:
		assert True
		
	try:
		invalid = os_data.os_match('linux', "nope", {})
	except ValueError:
		assert True

def test_os_match():
	data = os_data.os_info()

	if platform.system() == 'Linux':
		
		just_linux = os_data.os_match('linux')
		
		assert data.matches(just_linux) == True
		
		plat_data = platform.linux_distribution()
		
		if 'ubuntu' in plat_data[0].lower():
			
			ubuntu_match = os_data.os_match('linux', 'ubuntu')
			
			assert data.matches(ubuntu_match) == True
			
			ubuntu_match = os_data.os_match('linux', 'ubuntu', "=" + plat_data[1]) 
			
			assert data.matches(ubuntu_match) == True
			
		elif 'centos' in plat_data[0].lower():
			
			centos_match = os_data.os_match('linux', 'centos')
			assert data.matches(centos_match) == True
			centos_match = os_data.os_match('linux', 'centos', "=" + plat_data[1])
			assert data.matches(centos_match) == True
			centos_match = os_data.os_match('linux', 'centos', ">=" + plat_data[1])
			assert data.matches(centos_match) == True

def test_os_not_match():
	data = os_data.os_info()

	if platform.system() == 'Linux':
		
		just_linux = os_data.os_match('linux')
		
		assert data.matches(just_linux) == True
		
		plat_data = platform.linux_distribution()
		
		if 'ubuntu' in plat_data[0].lower():
			
			ubuntu_match = os_data.os_match('linux', 'centos')
			
			assert data.matches(ubuntu_match) == False
			
			ubuntu_match = os_data.os_match('linux', 'ubuntu', "<" + plat_data[1]) 
			
			assert data.matches(ubuntu_match) == False
			
		elif 'centos' in plat_data[0].lower():
			
			centos_match = os_data.os_match('linux', 'ubuntu')
			assert data.matches(centos_match) == False
			centos_match = os_data.os_match('linux', 'centos', "<" + plat_data[1])
			assert data.matches(centos_match) == False

	
