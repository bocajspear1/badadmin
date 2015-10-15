import util.os_data as os_data
import platform


def test_values():
	assert not os_data.LINUX.UBUNTU == None
	assert not os_data.LINUX.CENTOS == None

def test_os_info_obj():

	data = os_data.os_info()

	if platform.system() == 'Linux':
		assert data.os_type() == os_data.OS.LINUX

		plat_data = platform.linux_distribution()
		
		if 'ubuntu' in plat_data[0].lower():
			assert data.flavor() == os_data.LINUX.UBUNTU
			assert data.version() == plat_data[1]


def test_os_match():
	pass
