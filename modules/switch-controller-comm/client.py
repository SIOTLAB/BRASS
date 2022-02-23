#!/usr/bin/env python

import socket


TCP_IP = '10.16.224.22'
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(str.encode(MESSAGE))
data = s.recv(BUFFER_SIZE)
s.close()

print("received data:", data)
