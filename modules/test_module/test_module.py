# Import the base module
from ..base import module_base

class test_module(module_base):
	
	def __init__(self):
		super(test_module, self).__init__()

	def name(self):
		return "Test Module"
		
	def version(self):
		return "1.0.0"
		
	def author(self):
		return "Test Author" 


	def run(self):
		pass
		
	## Function for when a vulnerability is tested
	def test_run(self, vuln_obj, options={}):
		pass
