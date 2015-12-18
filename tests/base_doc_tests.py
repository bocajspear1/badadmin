import sys
import os
import util.version_util as version_util
sys.path.append("./modules") 

from base import doc

def test_valid_doc():
	
	test_obj = doc("module")
	
	try:
		
		test_obj.add_doc("TEST_VULN", "Did something")
		assert test_obj.get_all_docs(output='clear') == "Module: module [TEST_VULN] - Did something\n"
		assert test_obj.get_all_docs() == "TW9kdWxlOiBtb2R1bGUgW1RFU1RfVlVMTl0gLSBEaWQgc29tZXRoaW5nCg=="
		
	except ValueError:
		assert False
		
def test_invalid_doc():
	
	test_obj = doc("module")
	
	try:
		
		test_obj.add_doc({}, "Did something")
		assert False
		
	except ValueError:
		assert True
		
	try:
		
		test_obj.add_doc("A", [])
		assert False
		
	except ValueError:
		assert True

