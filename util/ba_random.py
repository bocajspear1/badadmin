import random
		
class ba_random():
	
	def array_random(self, array):
		array_size = len(array)
		if array_size > 0:
			r_key = self.random_number(0, array_size)
			return array[r_key] 
		else:
			return []

	def random_string(self, min=2, max=10):
	
		num = self.random_number(max - min)
		
		run_times = num + min
		
		rand_string = ""
		
		for i in range(run_times):
			rand_string += random.choice(string.ascii_letters)
	
		return rand_string
	
	def random_number(self, start, end):
		return random.randrange(start, end)

	def will_do(self):
		block = self.random_number(0, 4) + 1
		
		if block % 2 == 0:
			return True
		else:
			return False
