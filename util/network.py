## @package util.network
#
# Utilities for getting network information
#
import util.os_data as os_data
import util.simple_command as simple_command
import util.cross_version as cross_version
import socket 

import re

## Stores networking information for the current system
#
class networking(object):
	
	## Create a networking object
	#
	def __init__(self):
		self.__interfaces = {}
		self.__IPv4_LEN = 32
		self.__IPv6_LEN = 128
		self.__IPv4_BLOCK_LEN = 8
		self.__IPv6_BLOCK_LEN = 16
		self.__IPv4_BLOCK_COUNT = 4
		self.__IPv6_BLOCK_COUNT = 8
		
		self.__fill()
	
	# Fills the object with network information. Currently only supports Linux
	def __fill(self):
		
		if os_data.os_info().matches(os_data.os_match('linux')):
			cmd = simple_command.simple_command()
			code, output, errors = cmd.run("ip addr")
			
			if code == 0:
			
				output = "\n".join(output)
				
				raw_interfaces = re.split("\n[0-9]+: ", "\n" + output)
				
				for interface in raw_interfaces:
					if interface == "":
						continue
						
					data_split = interface.split(": ")
					
					interface_name = data_split[0]
					del data_split[0]
					interface_info = ": ".join(data_split)
					
					self.__interfaces[interface_name] = {}
					info_split = interface_info.split("\n")
					for line in info_split:
						if line.startswith("  "):
							line = line.strip()
							line_split = line.split(" ")
							if line.startswith("link"):
								if len(line_split) == 4:
									
									if not 'mac' in self.__interfaces[interface_name]:
										self.__interfaces[interface_name]['mac'] = {}
									
									self.__interfaces[interface_name]['mac']['address'] = line_split[1]
									self.__interfaces[interface_name]['mac']['broadcast'] = line_split[3]
									
							elif line.startswith("inet "):
								if len(line_split) >= 4:
									ipv4_data = line_split[1]
									ip_split = ipv4_data.split("/")
									
									addr = ip_split[0]
									mask = ip_split[1]
									
									if not 'ipv4' in self.__interfaces[interface_name]:
										self.__interfaces[interface_name]['ipv4'] = {}
									
									self.__interfaces[interface_name]['ipv4']['address'] = addr
									self.__interfaces[interface_name]['ipv4']['mask'] = mask
									if "brd" in line:
										self.__interfaces[interface_name]['ipv4']['broadcast'] = line_split[3]
									
							elif line.startswith("inet6 "):
								if len(line_split) >= 4:
									ipv6_data = line_split[1]
									ip_split = ipv6_data.split("/")
									
									addr = ip_split[0]
									mask = ip_split[1]
									
									if not 'ipv6' in self.__interfaces[interface_name]:
										self.__interfaces[interface_name]['ipv6'] = {}
									
									self.__interfaces[interface_name]['ipv6']['address'] = addr
									self.__interfaces[interface_name]['ipv6']['mask'] = mask
									if "brd" in line:
										self.__interfaces[interface_name]['ipv6']['broadcast'] = line_split[3]
					
				#~ print(self.__interfaces)
			else:
				print("Error running ip addr")
		elif os_data.os_info().matches(os_data.os_match('windows')):
			pass
	
	# Convert a mask to binary
	def __mask_to_binary(self, mask, length):
		if "." in mask:
			pass
		elif cross_version.isnumeric(mask):
			mask = int(mask)
			bin_mask = 0b0
			
			for i in range(mask):
				bin_mask = bin_mask << 1
				bin_mask = 0b1 | bin_mask
			
			for i in range(length - mask):
				bin_mask = bin_mask << 1
			
			return bin_mask
		else:
			raise ValueError("Invalid mask")
	
	# Convert IPv4 and IPv6 addresses to binary	
	def __address_to_binary(self, address):
		
		bin_addr = 0b0
		
		if "." in address:
			bin_addr = 0b0
			
			addr_list = address.split(".")
			for block in addr_list:
				if cross_version.isnumeric(block):
					block = int(block)
					bin_addr = bin_addr << 8
					bin_addr = bin_addr | block
				else:
					raise ValueError("Invalid IPv4 address")
			
			return bin_addr
			
		elif ":" in address:
			
			addr_split = address.split(":")
			
			if addr_split[0] == "" and addr_split[1] == "":
				del addr_split[0]
			
			if addr_split.count("") > 1:
				raise ValueError("Invalid IPv6 address")
			elif len(addr_split) - 1 < 8 and addr_split.count("") == 1:
				insert_count = 8 - len(addr_split)
				for i in range(insert_count + 1):
					addr_split.insert(addr_split.index(""), "0")
				
				addr_split.remove("")
			elif len(addr_split) < 8:
				raise ValueError("Invalid IPv6 address")
			
			for block in addr_split:
				block = int(block, 16)
				bin_addr = bin_addr << 16
				bin_addr = bin_addr | block
		
			
			return bin_addr
		else:
			raise ValueError("Invalid address")
	
	def __binary_to_IPv4(self, binary):
		
		addr_string = ""
		
		for i in range(self.__IPv4_BLOCK_COUNT):
			grab_mask = 0xFF
			
			block = binary & grab_mask

			if i < self.__IPv4_BLOCK_COUNT - 1:
				addr_string = "." + str(block) + addr_string
			else:
				addr_string = str(block) + addr_string
			
			binary = binary >> self.__IPv4_BLOCK_LEN
			
		return addr_string
	
	def __binary_to_IPv6(self, binary):
		
		addr_string = ""
		
		for i in range(self.__IPv6_BLOCK_COUNT):
			grab_mask = 0xFFFF
			
			block = binary & grab_mask

			if i < self.__IPv6_BLOCK_COUNT - 1:
				addr_string = ":" + format(block, 'x') + addr_string
			else:
				addr_string = format(block, 'x') + addr_string
			
			binary = binary >> self.__IPv6_BLOCK_LEN
			
		return addr_string
	
	## Get the IPv4 and IPv6 base network addresses for the given interface
	#
	# @param interface (string) - Name of interface to query the network address of
	# @returns tuple - (IPv4_ADDRESS, IPv6_ADDRESS)
	#
	def get_networks(self, interface):
		if interface in self.__interfaces:
			
			ipv4_network = None
			ipv6_network = None
			
			if 'ipv4' in self.__interfaces[interface]:
				mask4 = self.__interfaces[interface]['ipv4']['mask']
				
				bin_mask = self.__mask_to_binary(mask4, self.__IPv4_LEN)
				bin_addr = self.__address_to_binary(self.__interfaces[interface]['ipv4']['address'])
				
				bin_result = bin_mask & bin_addr

				ipv4_network = self.__binary_to_IPv4(bin_result)
				
			if 'ipv6' in self.__interfaces[interface]:
			
				bin_mask = self.__mask_to_binary(self.__interfaces[interface]['ipv6']['mask'], self.__IPv6_LEN)
				bin_addr = self.__address_to_binary(self.__interfaces[interface]['ipv6']['address'])
				
				
				bin_result = bin_mask & bin_addr
				
				ipv6_network = self.__binary_to_IPv6(bin_result)
				
			return (ipv4_network, ipv6_network)
	
	## Gets all available addresses for an interface
	#
	# @param interface (string) - Name of interface to query the addresses of
	# @returns dict - {mac, ipv4, ipv6} or None
	#
	def get_addresses(self, interface):
		if interface in self.__interfaces:
			return self.__interfaces[interface]
		else:
			return None
			
	## Gets a list of interfaces on the system
	#
	# @returns string[] - List of interfaces
	#	
	def get_interfaces(self):
		return list(self.__interfaces.keys())

	## Checks if a port is available on both IPv4 and IPv6
	# Port must be available on both IPv6 and IPv4
	#
	# #param port (int) - Port to test
	# @returns bool - True means port is available, False if not
	#
	def is_port_available(self, port):
		
		
		try:
			test_socket = socket.socket()
			test_socket.bind(('', port))
			
			test_socket = socket.socket(socket.AF_INET6)
			test_socket.bind(('', port))
			print(port)
			return True
		except:
			return False
