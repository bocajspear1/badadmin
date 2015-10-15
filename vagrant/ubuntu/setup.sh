apt-get -y update && apt-get -y upgrade
apt-get install -y python python3 python-pip python3-pip
pip install nose
pip3 install nose
echo 'python -m nose --nocapture --tests tests' > /usr/local/bin/nosetests2
echo 'python3 -m nose --nocapture --tests tests' > /usr/local/bin/nosetests3
echo 'echo -e "Python 2: \n"
nosetests2
echo -e "\n\nPython 3: \n"
nosetests3
' > /usr/local/bin/nosetests_both
chmod +x /usr/local/bin/nosetests2
chmod +x /usr/local/bin/nosetests3
chmod +x /usr/local/bin/nosetests_both
