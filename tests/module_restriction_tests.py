import util.module_util as module_util
import util.os_data as os_data

def test_version_restriction_ver():
	test_obj = module_util.import_module('test_module')
	
	vuln = test_obj.new_vulnerability("Restrict_Test_1", "Test", "restrict", "1.0.0")
	test_obj.add_vulnerability(vuln)

	assert len(test_obj.get_vulnerabilities()) == 1
	
	test_obj.add_version_restriction("restrict", ">=1.0")
	
	assert len(test_obj.get_vulnerabilities(force=True)) == 1

	test_obj.add_version_restriction("restrict", "<1.0")

	assert len(test_obj.get_vulnerabilities(force=True)) == 0

def test_version_restriction_temp_ver():
	test_obj = module_util.import_module('test_module')
	
	vuln = test_obj.new_vulnerability("Restrict_Test_1", "Test", "restrict", "1.0.0")
	test_obj.add_vulnerability(vuln)

	assert len(test_obj.get_vulnerabilities()) == 1
	
	test_obj._add_temp_version_restriction("restrict", ">=1.0")
	
	assert len(test_obj.get_vulnerabilities(force=True)) == 1

	test_obj._add_temp_version_restriction("restrict", "<1.0")

	assert len(test_obj.get_vulnerabilities(force=True)) == 0
	
	test_obj._clear_temp_restrictions()
	
	assert len(test_obj.get_vulnerabilities(force=True)) == 1
	
def test_version_restriction_level():
	test_obj = module_util.import_module('test_module')
	
	vuln = test_obj.new_vulnerability("Restrict_Test_1", "Test", "restrict", "1.0.0")
	vuln.set_difficulty("hard")
	test_obj.add_vulnerability(vuln)

	assert len(test_obj.get_vulnerabilities()) == 1
	
	HARD = 3
	EASY = 1
	
	test_obj.set_difficulty_limit(EASY)
	
	assert len(test_obj.get_vulnerabilities(force=True)) == 0

	test_obj.set_difficulty_limit(HARD)

	assert len(test_obj.get_vulnerabilities(force=True)) == 1

def test_version_restriction_dep():
	test_obj = module_util.import_module('test_module')
	
	vuln = test_obj.new_vulnerability("Restrict_Test_1", "Test", "restrict", "1.0.0")
	vuln.add_dependency(("test", ">2.0.0a"))
	test_obj.add_vulnerability(vuln)

	assert len(test_obj.get_vulnerabilities()) == 1
	
	test_obj.add_dependency_restriction("test", ">2.0.0")
	
	assert len(test_obj.get_vulnerabilities(force=True)) == 0

def test_version_restriction_dep_or():
	test_obj = module_util.import_module('test_module')
	
	vuln = test_obj.new_vulnerability("Restrict_Test_2", "Test", "restrict", "1.0.0")
	vuln.add_dependency([("test2", ">2.0.0b"), ("test", ">2.0.0a")])
	test_obj.add_vulnerability(vuln)

	assert len(test_obj.get_vulnerabilities()) == 1
	
	test_obj.add_dependency_restriction("test", ">2.0.0")
	
	assert len(test_obj.get_vulnerabilities(force=True)) == 1
	
	test_obj.add_dependency_restriction("test2", ">2.0.0")
	
	assert len(test_obj.get_vulnerabilities(force=True)) == 0

def test_version_restriction_os():
	test_obj = module_util.import_module('test_module')
	
	vuln = test_obj.new_vulnerability("Restrict_Test_OS", "Test", "restrict", "1.0.0")
	
	test_obj.add_vulnerability(vuln)
	
	assert len(test_obj.get_vulnerabilities(force=True)) == 1
	
	if os_data.os_info().matches(os_data.os_match('linux', 'ubuntu')):
		vuln.add_supported_os('linux', 'centos')
	else:
		vuln.add_supported_os('linux', 'ubuntu')
		
	
	assert len(test_obj.get_vulnerabilities(force=True)) == 0
	
