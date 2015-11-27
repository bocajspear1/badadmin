import util.cross_version as cross_version
import subprocess

## Provides simplified access to running commands on the system.
#
#
class simple_command():
	
	
	## Runs a command
	# 
	# @param string command_string - The command to run
	# @param string[] send_list - Input to be given during execution, each item in the list will be inputted with a newline (\\n) at the end
	# @returns (output_list, error_list) - the output and any reported errors, respectively
	#
	def run(self, command_string, send_list=[]):

		PYTHON_VERSION = cross_version.get_python_version()

		if not cross_version.isstring(command_string):
			raise ValueError("Invalid command")	
		
		proc = subprocess.Popen([command_string], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		
		if len(send_list) > 0:
			stdin_string = ""
			
			for value in send_list:
				stdin_string += value + "\n"
			
			if PYTHON_VERSION == 3:
				stdin_string = bytes(stdin_string, 'UTF-8')
		else:
			stdin_string = None
			
		try:
			if PYTHON_VERSION == 3:
				output, error = proc.communicate(stdin_string, timeout=60)
				output = output.decode('UTF-8')
				error = error.decode('UTF-8')
			elif PYTHON_VERSION == 2:
				output, error = proc.communicate(stdin_string)
		
		
			if not output.strip() == "":
				output_list = output.strip().split("\n")
			else:
				output_list = []
				
			if not error.strip() == "":
				error_list = error.strip().split("\n")
			else:
				error_list = []
			
			if '' in output_list:
				output_list.remove('')
			
			if '' in error_list:
				error_list.remove('')
			
			return (proc.returncode ,output_list, error_list)
		except OSError as e:
			return ([], ["OSError", e.message])
		
