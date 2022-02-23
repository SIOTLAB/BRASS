#!/usr/bin/env python

import socket 
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

IP = '127.0.0.1'
PORT = 9434
server_address = (IP, PORT)
sock.bind(server_address)
response = 'pfg_ip_response_serv'

while True:
	data, address = sock.recvfrom(4096)
	data = str(data.decode('UTF-8'))
	#print('Received ' + str(len(data)) + ' bytes from ' + str(address) )
	#print('Data:' + data)
	
	if data == 'pfg_ip_broadcast_cl':
		#print('responding...')
		sent = sock.sendto(response.encode(), address)
		#print('Sent confirmation back')
