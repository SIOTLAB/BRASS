#!/usr/bin/env python

import json
import socket 
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

IP = '127.0.0.255'
PORT = 9434
server_address = (IP, PORT)
sock.bind(server_address)
msgPrefix = 'pfg_ip_broadcast_cl'
svrPrefix = 'pfg_ip_response_serv'

try:
	while True:
		data, address = sock.recvfrom(4096)
		data = str(data.decode())
		
		if data.startswith(msgPrefix):
			data = data[len(msgPrefix):]
			data = json.loads(data.decode('UTF-8'))

			print('received:')
			print('\tdestination: ' + data['dest'])
			print('\treservation: ' + str(data['resv']))
			print('\tduration: ' + str(data['dura']))
			sent = sock.sendto(svrPrefix.encode(), address)
except KeyboardInterrupt:
	print('close')
	sock.close()