## @package util.ba_random
#
# High level randomization functions
#
import random
import string
## @class ba_random
#
# Class provides high-level randomization functions
#
class ba_random():
	
	## Returns a single random item from an array
	#
	# @param array (object[]) - Values to select random value from
	# @returns object - Random value from array
	#
	def array_random(self, array):
		array_size = len(array)
		if array_size > 0:
			r_key = self.random_number(0, array_size - 1)
			return array[r_key] 
		else:
			return None
	
	## Returns string of random ASCII characters
	#
	# @param min (int) - [optional] Minimum size of the string
	# @param max (int) - [optional] Maximum size of the string
	# @returns string - Random string
	#
	def random_string(self, min=2, max=10):
	
		num = self.random_number(0, max - min)
		
		run_times = num + min
		
		rand_string = ""
		
		for i in range(run_times):
			rand_string += random.choice(string.ascii_letters)
	
		return rand_string
	
	## Returns a random number where the result N is end <= N >= start
	#
	# @param start (int) - Start of possible range
	# @param end (int) - End of possible range (inclusive)
	# @returns int - Random integer
	#
	def random_number(self, start, end):
		return random.randint(start, end)

	## Simple function to test for True or False
	# Used to indicate if something will or will not be done
	#
	# @returns bool
	#
	def will_do(self):
		i = self.random_number(0, 1)
		
		if i == 1:
			return True
		elif i == 0:
			return False
		else:
			raise ValueError("Invalid")
