#!/usr/bin/env python3

#  import socket

#  HOST = '127.0.1.1'
#  PORT = 65432

#  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#      s.connect((HOST, PORT))
#      s.sendall(b'Hello world!')
#      data = s.recv(1024)

#  print('Received', repr(data))

from socket import socket, AF_INET, SOCK_DGRAM, \
    gethostbyname_ex, gethostname
from select import select

PORT = 50000
MAGIC = "Jts45F2t8cMgrNT2"

s = socket(AF_INET, SOCK_DGRAM)  # create UDP socket
s.bind(('', PORT))
s.setblocking(False)

my_ip = gethostbyname_ex(gethostname())

while 1:
    ready = select([s], [], [], 1)
    if ready[0]:
        data, addr = s.recvfrom(1024)  # wait for a packet
        if data.startswith(MAGIC.encode()):
            print("Got service announcement from",
                  data[len(MAGIC)+1:-1].decode().split(',')[2])
            #  s.sendto(str.encode("Hello from client"), (data[2], PORT))

            #  Send the client's IP and PORT
            #  Connect to the server's IP and PORT

            break
    else:
        print("timeout")
