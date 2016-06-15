from util.network import networking
from util.simple_command import simple_command
import util.os_data as os_data

def test_get_interfaces():
	test_obj = networking()
	if os_data.os_info().matches(os_data.os_match('linux')):
		value = test_obj.get_interfaces()
		assert "lo" in value
	
def test_get_network():
	test_obj = networking()
	if os_data.os_info().matches(os_data.os_match('linux')):
		value = test_obj.get_networks("lo")
		assert value[0] == "127.0.0.0"
		assert value[1] == "0:0:0:0:0:0:0:1"
		value = test_obj.get_networks("eth0")
		
def test_get_addresses():
	test_obj = networking()
	if os_data.os_info().matches(os_data.os_match('linux')):
		value = test_obj.get_addresses("lo")
		assert 'mac' in value
		assert 'ipv4' in value
		assert 'ipv6' in value
		
		assert value['mac']['address'] == "00:00:00:00:00:00"
		assert value['mac']['broadcast'] == "00:00:00:00:00:00"
		
		assert value['ipv4']['address'] == "127.0.0.1"
		assert value['ipv4']['mask'] == "8"
		
		assert value['ipv6']['address'] == "::1"
		assert value['ipv6']['mask'] == "128"

def test_available_ports():
	test_obj = networking()
	
	port_list = []
	
	if os_data.os_info().matches(os_data.os_match('linux')):
		code, output, error = simple_command().run('netstat -tunap | grep LISTEN')
		
		for line in output:
			line_list = line.split(" ")
			
			new_line = []
			
			for item in line_list:
				if item != "":
					new_line.append(item)
			
			listen_section = new_line[3]
			
			listen_split = listen_section.split(":")
			
			port = listen_split[len(listen_split) - 1]
			
			port_list.append(int(port))
	
		for port in port_list:
			assert test_obj.is_port_available(port) == False

		i = 1
		for j in range(5): 
			while i in port_list and i <= 65535:
				i += 5
			
			if i == 65535:
				assert False
			
			assert test_obj.is_port_available(i) == True
			i += 5
