import argparse
import os 
import util.module_util
import util.resolve
import sys

parser = argparse.ArgumentParser(description='Test a vulnerability in a module on the current system')
parser.add_argument("module", nargs=1,help="Name of module")
parser.add_argument("vulnerability", nargs=1,help="Name of vulnerability to run")
parser.add_argument('options', nargs='+', help="Name of vulnerability to run")

args = parser.parse_args()
#print(args.options)

if os.geteuid() != 0:
	print ("\nYou need to be root to test a vulnerability")
	sys.exit()

mod_result = util.module_util.import_module(args.module[0])

if mod_result == False:
	print("Module '" + args.module[0] + "' does not exist")
else:
	vuln_result = mod_result.get_vulnerability_object(args.vulnerability[0])
	if vuln_result == False:
		print("Vulnerability '" + args.vulnerability[0] + "' does not exist")
	else:
		
		option_input = {}
		
		for option in args.options:
			option_list = option.split("=")
			option_input[option_list[0].strip()] = option_list[1].strip()
			
		print(option_input)
		
		status = mod_result.test_run(vuln_result, option_input)	
		
		if status == False:
			print("Vulnerabilty test failed")
		elif status == True:
			print("Vulnerabilty succeeded")
			
			doc_output = mod_result.doc.base64_doc()
			print(doc_output)
		else:
			print("Got unexpected value")
