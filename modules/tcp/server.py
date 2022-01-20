#!/usr/bin/env python3

#  import socket

#  HOST = '127.0.1.1'
#  PORT = 65432

#  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#      s.bind((HOST, PORT))
#      s.listen()
#      conn, addr = s.accept()
#      with conn:
#          print('Connected by', addr)
#          while True:
#              data = conn.recv(1024)
#              if not data:
#                  break
#              conn.sendall(data)

from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, \
    gethostbyname_ex, gethostname
from time import sleep

PORT = 50000
MAGIC = "Jts45F2t8cMgrNT2"

s = socket(AF_INET, SOCK_DGRAM)  # create UDP socket
s.bind(('', 0))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  # this is a broadcast socket
my_ip = gethostbyname_ex(gethostname())

while 1:
    data = MAGIC + str(my_ip)
    s.sendto(data.encode(), ('<broadcast>', PORT))
    print('sent service announcement')
    sleep(2)

    #  s.recvall()
