# Test file for base.py file

# Insert the module into the path

import sys
import os
import getpass
import pwd

from util.simple_filesystem import simple_file

if os.geteuid() != 0:
	print ("\n\n! - You need to be root to run file tests\n")
	sys.exit()

def test_file_create_valid():
	
	path = "/tmp/badadmin-tests"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	
	assert isinstance(test_file, simple_file) == True
	assert test_file.create() == True
	assert os.path.exists(path) == True
	assert test_file.remove() == True
	assert os.path.exists(path) == False

def test_file_create_invalid():
	
	path = "/tmp/nope/badadmin-tests"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	
	assert isinstance(test_file, simple_file) == True
	assert test_file.create() == False
	assert os.path.exists(path) == False
	
	
def test_file_on_dir():
	path = "/tmp"
	
	assert os.path.exists(path) == True
	
	
	
	
	
	try:
		test_file = simple_file(path)
		assert False
	except ValueError:
		assert True
			

def test_file_create_blank():
	
	try:
		test_file = simple_file("")
		assert False
	except ValueError:
		assert True

def test_file_add_content():
	
	path = "/tmp/badadmin-tests-content"
	content = "This is a test!\n"
	content2 = "Another test!\n"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert os.path.exists(path) == True
	
	assert test_file.write_contents(content) == True

	assert test_file.get_contents() == content
	
	ensure = open(path, "r")
	assert ensure.read() == content
	ensure.close()
	
	assert test_file.write_contents(content2) == True
	
	assert test_file.get_contents() == content2
	
	ensure = open(path, "r")
	assert ensure.read() == content2
	ensure.close() 

	assert test_file.remove() == True

def test_file_dont_clobber():
	
	path = "/tmp/badadmin-tests-clobber"
	content = "Clobber?\n"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert test_file.write_contents(content) == True
	
	ensure = open(path, "r")
	assert ensure.read() == content
	ensure.close() 
	
	assert os.path.exists(path) == True
	
	test_file2 = simple_file(path)

	assert test_file2.create() == False
	
	ensure = open(path, "r")
	assert ensure.read() == content
	ensure.close() 
	
	assert os.path.exists(path) == True
	assert test_file.remove()

def test_file_do_clobber():
	
	path = "/tmp/badadmin-tests-clobber2"
	content = "Clobber?\n"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert test_file.write_contents(content) == True
	
	assert test_file.get_contents() == content
	
	assert os.path.exists(path) == True
	
	test_file2 = simple_file(path)

	assert test_file2.create(clobber=True) == True
	
	ensure = open(path, "r")
	assert ensure.read() == ""
	ensure.close() 
	
	assert os.path.exists(path) == True
	assert test_file.remove()


def test_file_move():
	
	path = "/tmp/badadmin-tests-copy1"
	path2 = "/tmp/badadmin-tests-copy2"
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert os.path.exists(path) == True
	
	test_file.move(path2)
	
	assert os.path.exists(path) == False
	assert os.path.exists(path2) == True

	test_file2 = simple_file(path2)
	assert test_file2.remove() == True
	assert test_file.remove() == False

def test_file_copy_nokeep():
	
	path = "/tmp/badadmin-tests-copy1"
	path2 = "/tmp/badadmin-tests-copy2"
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert os.path.exists(path) == True
	
	test_file.copy(path2)
	
	assert os.path.exists(path) == True
	assert os.path.exists(path2) == True

	
	test_file2 = simple_file(path2)
	assert test_file2.remove() == True
	assert test_file.remove() == True
	
# Need to test copy with keeping file metadata

def test_file_append():
	
	path = "/tmp/badadmin-tests-append"
	content = "Start\n"
	content2 = "Addition\n"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert os.path.exists(path) == True
	
	assert test_file.write_contents(content) == True

	assert test_file.get_contents() == content
	
	assert test_file.append_content(content2) == True
	
	assert test_file.get_contents() == content + content2
	
	ensure = open(path, "r")
	assert ensure.read() == content + content2
	ensure.close() 

	assert test_file.remove() == True

def test_file_replace():
	
	path = "/tmp/badadmin-tests-replace"
	content = "ReplaceMe\nReplaceMe\nNope\nReplaceMe\n"
	replace_with = "Done!"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert os.path.exists(path) == True
	
	assert test_file.write_contents(content) == True

	assert test_file.get_contents() == content
	
	new_content = test_file.replace("ReplaceMe", replace_with) 

	assert new_content == "Done!\nDone!\nNope\nDone!\n"

	assert test_file.remove() == True

def test_file_regex_replace():
	
	path = "/tmp/badadmin-tests-replace-regex"
	content = "ReplaceMe1\nReplaceMe2\nNope\nReplaceMe3\n"
	pattern = "ReplaceMe[0-9]{1}"
	replace_with = "Done!"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert os.path.exists(path) == True
	
	assert test_file.write_contents(content) == True

	assert test_file.get_contents() == content
	
	new_content = test_file.regex_replace(pattern, replace_with) 

	
	assert new_content == "Done!\nDone!\nNope\nDone!\n"

	assert test_file.remove() == True

def test_file_exists():
	
	path = "/tmp/badadmin-tests-replace-exists"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert os.path.exists(path) == True
	assert test_file.exists() == True

	assert test_file.remove() == True


def test_file_owner():
	
	my_uid = os.getuid()
	my_gid = os.getgid()
	
	path = "/tmp/badadmin-tests-owner"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert os.path.exists(path) == True
	assert test_file.exists() == True
	
	ownership = test_file.get_ownership()
	
	assert ownership['uid'] == my_uid
	assert ownership['gid'] == my_gid
	
	assert ownership['owner_name'] == getpass.getuser()
	assert ownership['group_name'] == getpass.getuser()
	

	assert test_file.remove() == True

def test_file_set_owner():
	
	uid1 = pwd.getpwuid(1).pw_name
	uid2 = pwd.getpwuid(2).pw_name
	
	my_uid = os.getuid()
	my_gid = os.getgid()
	
	path = "/tmp/badadmin-tests-owner2"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert os.path.exists(path) == True
	assert test_file.exists() == True
	
	test_file.set_ownership_by_id(1, 1)
	
	ownership = test_file.get_ownership()
	
	assert ownership['uid'] == 1
	assert ownership['gid'] == 1
	
	assert ownership['owner_name'] == uid1
	assert ownership['group_name'] == uid1
	
	test_file.set_ownership_by_name(uid2, uid2)
	
	ownership = test_file.get_ownership()

	
	assert ownership['owner_name'] == uid2
	assert ownership['group_name'] == uid2
	
	assert ownership['uid'] == 2
	assert ownership['gid'] == 2
	
	assert test_file.remove() == True

def test_file_permissions():
	
	
	path = "/tmp/badadmin-tests-permissions"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert os.path.exists(path) == True
	assert test_file.exists() == True
	
	permissions = test_file.get_permissions()
	
	assert permissions['owner'] >= 0 and permissions['owner'] <= 7
	assert permissions['group'] >= 0 and permissions['group'] <= 7
	assert permissions['other'] >= 0 and permissions['other'] <= 7
	assert permissions['special'] >= 0 and permissions['special'] <= 7

	assert test_file.remove() == True

def test_file_permissions_set():
	
	
	path = "/tmp/badadmin-tests-permissions-set"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert os.path.exists(path) == True
	assert test_file.exists() == True
	
	permissions = test_file.get_permissions()
	
	assert permissions['owner'] >= 0 and permissions['owner'] <= 7
	assert permissions['group'] >= 0 and permissions['group'] <= 7
	assert permissions['other'] >= 0 and permissions['other'] <= 7
	assert permissions['special'] >= 0 and permissions['special'] <= 7

	assert test_file.set_permissions(6,0,0,0) == True
	
	permissions = test_file.get_permissions()
	
	assert permissions['owner'] == 6
	assert permissions['group'] == 0
	assert permissions['other'] == 0
	assert permissions['special'] == 0
	
	assert test_file.set_permissions(6,0,0,1) == True
	
	permissions = test_file.get_permissions()
	
	assert permissions['owner'] == 6
	assert permissions['group'] == 0
	assert permissions['other'] == 0
	assert permissions['special'] == 1
	
	assert test_file.set_permissions(7,7,7,0) == True
	
	permissions = test_file.get_permissions()
	
	assert permissions['owner'] == 7
	assert permissions['group'] == 7
	assert permissions['other'] == 7
	assert permissions['special'] == 0
	
	assert test_file.remove() == True


def test_file_permissions_set_invalid():
	
	path = "/tmp/badadmin-tests-permissions-invalid"
	
	assert os.path.exists(path) == False
	
	test_file = simple_file(path)
	assert test_file.create() == True
	
	assert os.path.exists(path) == True
	assert test_file.exists() == True
	
	permissions = test_file.get_permissions()
	
	orig_owner = permissions['owner']
	orig_group = permissions['group']
	orig_other = permissions['other']
	orig_special = permissions['special']
	

	assert test_file.set_permissions(8,0,0,0) == False
	
	permissions = test_file.get_permissions()
	
	assert orig_owner == permissions['owner']
	assert orig_group == permissions['group']
	assert orig_other == permissions['other']
	assert orig_special == permissions['special']
	
	assert test_file.set_permissions(2,0,0,-1) == False
	
	permissions = test_file.get_permissions()
	
	assert orig_owner == permissions['owner']
	assert orig_group == permissions['group']
	assert orig_other == permissions['other']
	assert orig_special == permissions['special']
	
	assert test_file.set_permissions(2,10,-4,0) == False
	
	permissions = test_file.get_permissions()
	
	assert orig_owner == permissions['owner']
	assert orig_group == permissions['group']
	assert orig_other == permissions['other']
	assert orig_special == permissions['special']
	
	assert test_file.remove() == True
