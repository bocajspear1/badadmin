# WARNING!
# This module is used for unit testing and should not be used as an example!
#
import sys
# Import the base module
from ..base import module_base
from ..base import init

init()

import cross_version
import simple_filesystem

class test_module(module_base):
	
	def __init__(self):
		self.__name = "Test Module"
		self.__class = "test_module"
		super(test_module, self).__init__()
		
		
		
	def name(self):
		return self.__name
		
	def version(self):
		return "1.0.0"
		
	def author(self):
		return "Test Author" 

	def description(self):
		return "Test Description"

	def run(self):
		pass

	def set_name(self, name):
		if self.cross_version().isstring(name):
			self.__name = name

	
	def override_class_name(self, name):
		if self.cross_version().isstring(name):
			self.__class = name
	
	def get_class_name(self):
		return self.__class
