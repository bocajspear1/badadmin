import util.cross_version as cross_version

def get_python_version_tests():
	assert cross_version.get_python_version() == 2 or cross_version.get_python_version() == 3

def isstring_tests():
	assert cross_version.isstring("hi there") == True
	assert cross_version.isstring('wassup') == True
	assert cross_version.isstring({"nope": "nope"}) == False
	assert cross_version.isstring(['i']) == False
	
def isinteger_tests():
	assert cross_version.isinteger("hi there") == False
	assert cross_version.isinteger(1) == True
	assert cross_version.isinteger(1.01) == False
	assert cross_version.isinteger({1: 2}) == False
	
		

def enum_tests():
	
	test_enum = cross_version.Enum(['a','b', 'c'])
	
	assert test_enum.a == "a"
	assert test_enum.b == "b"
	try:
		test_enum.a = "nope"
		assert False
	except AttributeError:
		assert True
		assert test_enum.a == "a"
