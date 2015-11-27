yum update -y
yum install -y epel-release
yum install -y python python-pip
pip install nose
echo 'nosetests -v ./tests' > /usr/local/bin/nosetests2
chmod +x /usr/local/bin/nosetests2
