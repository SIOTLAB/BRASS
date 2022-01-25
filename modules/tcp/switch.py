#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, IPPROTO_UDP, SO_REUSEADDR, SO_BROADCAST, gethostbyname_ex, gethostname
from select import select

PORT = 50000
MAGIC = "Jts45F2t8cMgrNT2"

s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)    # create UDP socket
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)    # allow multiple sockets to use this address
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)    # this is a broadcast socket
s.bind(('', PORT))
s.setblocking(False)

my_id = gethostbyname_ex(gethostname())
my_name = my_id[0]
my_ip = my_id[2][0]

while 1:
    ready = select([s], [], [], 1)
    if ready[0]:
        data, addr = s.recvfrom(1024)  # wait for a packet
        if data.startswith(MAGIC.encode()):
            print("Got service request from", data[len(MAGIC)+1:-1].decode().split(',')[2])

            print(data[2]);
            #  Send the switch's IP and PORT
            # s.sendto(str.encode("Hello from client"), (data[2], PORT))
            #  Connect to the controllers's IP and PORT

            break
    else:
        print("timeout")
