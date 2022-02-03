#!/usr/bin/env python

import os
import socket
import sys
import subprocess

# FOR TESTING VIA LAPTOP IN VLAN OF RACK 224
# myIP = str(os.popen("ifconfig tun0 | grep 'inet ' | awk '{print $2}'").read().decode())
# myIP = os.popen("ifconfig tun0 | grep 'inet ' | awk '{print $2}'").read()
myIP = '10.16.252.10'
###

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# server_address = ('10.16.252.11', 9434)
server_address = (myIP, 9434)

sock.bind(server_address)
print('Server bound on:', myIP, 9434)

message = 'pfg_ip_response_serv'
response = 'pfg_ip_broadcast_cl'

while True:
    data, address = sock.recvfrom(4096)
    data = str(data.decode('UTF-8'))

    if data == response:
        sent = sock.sendto(message.encode(), address)
	
	print(address[0])