from util.network import networking
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
