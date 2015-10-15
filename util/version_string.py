import util.cross_version as cross_version



def is_range(value):
	if not cross_version.isstring(value):
		return False
	
	if value == "*" or value == "-":
		return True
	
	if not (value.startswith(">") or value.startswith("<") or value.startswith("=")) or len(value) < 2:
		return False
	
	
	return True

## Compares the given input string to the current vulnerability's
# version. Returns a number (1-, 0, 1) based on the relation of the input
# version to the internal version. Does not take versions with >/</= in
# front of them, will throw an error
#
# -1 = The inputted version is lower then the internal version
# 0 = The inputted version is equal to the internal version
# 1 = the inputted version is greater the than the internal version
# 
# @param {string} version - The version to compare
# @returns {integer}
#	
def compare_version(test_version, comparison_version):
	
	if not cross_version.isstring(test_version) or not cross_version.isstring(comparison_version):
		raise ValueError("Versions must be strings")
	
	if not test_version.startswith(">") and not test_version.startswith("<") and not test_version.startswith("="):
		if test_version > comparison_version:
			return 1
		elif test_version == comparison_version:
			return 0
		elif test_version < comparison_version:
			return -1
		else:
			raise ValueError("Range found where version expected")	
		
	else:
		raise ValueError("Invalid version")	
	
## Tests vulnerability version against a given version to see if the vulnerability
# version falls within the bounds of the inputted version
#
# @param {string} version_range - The version string to test the vulnerability against
# @returns {boolean} = True if the vulnerabilty version passes, False if it does not
#
def test_range(version_range, test_version):
	
	if not cross_version.isstring(version_range):
		raise ValueError("Invalid version comparison")	
	
	if version_range.startswith("<="):
		only_version = version_range[2:]
		if test_version <= only_version:
			return True
		else:
			return False
	elif version_range.startswith(">="):
		only_version = version_range[2:]
		if test_version >= only_version:
			return True
		else:
			return False
	elif version_range.startswith("<"):
		only_version = version_range[1:]
		if test_version < only_version:
			return True
		else:
			return False
	elif version_range.startswith(">"):
		only_version = version_range[1:]
		if test_version > only_version:
			return True
		else:
			return False
	
	elif version_range.startswith("="):
		only_version = version_range[1:]
		if test_version == only_version:
			return True
		else:
			return False
	else:
		if test_version == version_range:
			return True
		else:
			return False
