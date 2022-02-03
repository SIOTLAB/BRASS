#!/usr/bin/env python

import socket
import time

SOCK = socket.socket()
IP = socket.gethostname()
NAME = socket.gethostbyname(IP)
HOST = "127.0.0.1"
PORT = 9434
MESSAGE = "pfg_ip_response_serv"
RESPONSE = "pfg_ip_broadcast_cl"

try:
    SOCK.connect((HOST, PORT))
except socket.error as e:
    print(str(e))

response = SOCK.recv(1024)

#  while True:
SOCK.send(str.encode(MESSAGE))
response = SOCK.recv(1024)
print(response.decode("utf-8"))

time.sleep(5)
SOCK.send(str.encode(IP + "," + HOST))
response = SOCK.recv(1024)
print(response.decode("utf-8"))

SOCK.close()
