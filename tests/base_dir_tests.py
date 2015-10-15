# Test file for base.py file

# Insert the module into the path

import sys
import os
import getpass

from util.simple_filesystem import simple_file
from util.simple_filesystem import simple_dir


test_location = "/tmp"

if os.geteuid() != 0:
	print ("\n\n! - You need to be root to run file tests\n")
	sys.exit()

def test_dir_create_valid():
	
	path = "/tmp/badadmin-dir-1"
	
	assert os.path.exists(path) == False
	
	test_dir = simple_dir(path)
	
	assert test_dir.exists() == False
	
	assert test_dir.create() == True
	
	assert os.path.exists(path) == True
	assert os.path.isdir(path) == True
	
	assert test_dir.remove() == True
	
def test_dir_create_invalid():
	
	path = test_location + "/nada/nope/badadmin-dir-2"
	
	assert os.path.exists(path) == False
	
	test_dir = simple_dir(path)
	
	assert test_dir.exists() == False
	
	assert test_dir.create() == False
	
	assert os.path.exists(path) == False
	assert os.path.isdir(path) == False
	
	assert test_dir.remove() == False

def test_dir_content():
	
	path = test_location + "/badadmin-dir-content"
	
	files = ['file1' , 'file2']
	
	
	
	assert os.path.exists(path) == False
	
	test_dir = simple_dir(path)
	
	assert test_dir.exists() == False
	
	assert test_dir.create() == True
	
	for item in files:
		current_file = simple_file(path + "/" + item)
		assert current_file.create() == True
	
	assert os.path.exists(path) == True
	assert os.path.isdir(path) == True
	
	assert len(test_dir.list()) == 2
	assert 'file1' in test_dir.list()
	assert 'file2' in test_dir.list()
	
	assert test_dir.remove() == True
	
	assert os.path.exists(path) == False
	assert os.path.isdir(path) == False


def test_dir_copy():

	path1 = "/tmp/badadmin-dir-cp1"
	path2 = "/tmp/badadmin-dir-cp2"
	
	assert os.path.exists(path1) == False
	
	test_dir = simple_dir(path1)
	test_dir.create()
	
	assert os.path.exists(path1) == True
	
	test_dir.copy(path2)
	
	assert os.path.exists(path1) == True
	assert os.path.exists(path2) == True
	
	rm_dir = simple_dir(path2)
	
	assert test_dir.remove() == True
	assert rm_dir.remove() == True

def test_dir_move():

	path1 = "/tmp/badadmin-dir-mv1"
	path2 = "/tmp/badadmin-dir-mv2"
	
	assert os.path.exists(path1) == False
	
	test_dir = simple_dir(path1)
	test_dir.create()
	
	assert os.path.exists(path1) == True
	
	test_dir.move(path2)
	
	assert os.path.exists(path1) == False
	assert os.path.exists(path2) == True
	
	rm_dir = simple_dir(path2)
	
	assert rm_dir.remove() == True
	
def test_dir_recursive_chmod():
	
	path = test_location + "/badadmin-r-chmod"
	
	dirs = ['dir1' , 'dir2']
	
	files = ['file1', 'file2']
	
	assert os.path.exists(path) == False

	test_dir = simple_dir(path)
	
	test_dir.create()
	
	assert os.path.exists(path) == True
	
	test_dir2 = simple_dir(path + "/" + dirs[0])
	test_dir2.create()
	assert os.path.exists(path + "/" + dirs[0]) == True
	test_dir3 = simple_dir(path + "/" + dirs[1])
	test_dir3.create()
	assert os.path.exists(path + "/" + dirs[1]) == True

	test_file1 = simple_file(path + "/" + files[0])
	test_file1.create()
	assert os.path.exists(path + "/" + files[0]) == True 
	
	test_file2 = simple_file(path + "/" + dirs[1] + "/" + files[0])
	test_file2.create()
	assert os.path.exists(path + "/" + dirs[1] + "/" + files[0]) == True 
	
	test_file3 = simple_file(path + "/" + dirs[0] + "/" + files[0])
	test_file3.create()
	assert os.path.exists(path + "/" + dirs[0] + "/" + files[0]) == True 
	
	test_file4 = simple_file(path + "/" + dirs[0] + "/" + files[1])
	test_file4.create()
	assert os.path.exists(path + "/" + dirs[0] + "/" + files[1]) == True 
	
	
	test_dir.recursive_chmod(7,0,0)
	
	permissions = test_dir.get_permissions()
	
	
	assert permissions['owner'] == 7
	assert permissions['group'] == 0
	assert permissions['other'] == 0
	assert permissions['special'] == 0
	
	permissions = test_file4.get_permissions()
	
	
	assert permissions['owner'] == 7
	assert permissions['group'] == 0
	assert permissions['other'] == 0
	assert permissions['special'] == 0
	
	permissions = test_file1.get_permissions()
	
	assert permissions['owner'] == 7
	assert permissions['group'] == 0
	assert permissions['other'] == 0
	assert permissions['special'] == 0
	
	assert test_dir.remove() == True



def test_dir_recursive_chmod():
	
	path = test_location + "/badadmin-r-chown"
	
	dirs = ['dir1' , 'dir2']
	
	files = ['file1', 'file2']
	
	assert os.path.exists(path) == False

	test_dir = simple_dir(path)
	
	test_dir.create()
	
	assert os.path.exists(path) == True
	
	test_dir2 = simple_dir(path + "/" + dirs[0])
	test_dir2.create()
	assert os.path.exists(path + "/" + dirs[0]) == True
	test_dir3 = simple_dir(path + "/" + dirs[1])
	test_dir3.create()
	assert os.path.exists(path + "/" + dirs[1]) == True

	test_file1 = simple_file(path + "/" + files[0])
	test_file1.create()
	assert os.path.exists(path + "/" + files[0]) == True 
	
	test_file2 = simple_file(path + "/" + dirs[1] + "/" + files[0])
	test_file2.create()
	assert os.path.exists(path + "/" + dirs[1] + "/" + files[0]) == True 
	
	test_file3 = simple_file(path + "/" + dirs[0] + "/" + files[0])
	test_file3.create()
	assert os.path.exists(path + "/" + dirs[0] + "/" + files[0]) == True 
	
	test_file4 = simple_file(path + "/" + dirs[0] + "/" + files[1])
	test_file4.create()
	assert os.path.exists(path + "/" + dirs[0] + "/" + files[1]) == True 
	
	
	test_dir.recursive_chown_by_id(1,1)
	
	ownership = test_dir.get_ownership()
	
	assert ownership['uid'] == 1
	assert ownership['gid'] == 1
	
	assert ownership['owner_name'] == 'daemon'
	assert ownership['group_name'] == 'daemon'
	
	ownership = test_file3.get_ownership()
	
	assert ownership['uid'] == 1
	assert ownership['gid'] == 1
	
	assert ownership['owner_name'] == 'daemon'
	assert ownership['group_name'] == 'daemon'
	
	ownership = test_file2.get_ownership()
	
	assert ownership['uid'] == 1
	assert ownership['gid'] == 1
	
	assert ownership['owner_name'] == 'daemon'
	assert ownership['group_name'] == 'daemon'
	
	test_dir.recursive_chown_by_name('bin', 'bin')
	
	ownership = test_dir.get_ownership()
	
	assert ownership['uid'] == 2
	assert ownership['gid'] == 2
	
	assert ownership['owner_name'] == 'bin'
	assert ownership['group_name'] == 'bin'
	
	ownership = test_file3.get_ownership()
	
	
	assert ownership['uid'] == 2
	assert ownership['gid'] == 2
	
	assert ownership['owner_name'] == 'bin'
	assert ownership['group_name'] == 'bin'
	
	ownership = test_dir2.get_ownership()
	
	assert ownership['uid'] == 2
	assert ownership['gid'] == 2
	
	assert ownership['owner_name'] == 'bin'
	assert ownership['group_name'] == 'bin'
	
	assert test_dir.remove() == True
