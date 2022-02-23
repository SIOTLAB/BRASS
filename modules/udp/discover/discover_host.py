#!/usr/bin/env python

import argparse
from socket import *
import sys
import time

# PARSE ARGUMENTS
parser = argparse.ArgumentParser(description='Request an amount of reservation from a network controller.')
parser.add_argument('dest', metavar='A.B.C.D', type=str,
                    help='destination IP for reserved communication')
parser.add_argument('resv', metavar='KB', type=int,
                    help='amount of bandwidth reservation in KiloBytes')
parser.add_argument('dura', metavar='sec', type=float,
                    help='duration of reservation in seconds')

args = parser.parse_args()

# CREATE UDP SOCKET
sock = socket(AF_INET, SOCK_DGRAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
sock.settimeout(5)

IP = '127.0.0.1'
PORT = 9434
server_address = (IP, PORT)
message = 'pfg_ip_broadcast_cl'

try:
	while True:
		# SEND DATA
		print('sending: ' + message)
		sent = sock.sendto(message.encode(), server_address)

		# RECEIVE RESPONSE
		print('waiting to receive')
		data, server = sock.recvfrom(4096)
		if data.decode('UTF-8') == 'pfg_ip_response_serv':
			print('Received confirmation')
			print('Server ip: ' + str(server[0]) )
			break
		else:
			print('Verification failed')
		
		print('Trying again...')
	
	
finally:	
	sock.close()
