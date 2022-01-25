#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, IPPROTO_UDP, SO_REUSEADDR, SO_BROADCAST, SO_BINDTODEVICE, gethostbyname_ex, gethostname
from time import sleep

PORT = 50000
MAGIC = "Jts45F2t8cMgrNT2"

my_id = gethostbyname_ex(gethostname())
my_name = my_id[0]
my_ip = my_id[2][0]

s = socket(AF_INET, SOCK_DGRAM)    # create UDP socket
s.bind((my_ip, PORT))
# s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)    # create UDP socket
# s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)    # allow multiple sockets to use this address
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)    # this is a broadcast socket
# s.setsockopt(SOL_SOCKET, SO_BINDTODEVICE, str.encode('ma1' + '\0'))
s.settimeout(2)

while 1:
    data = MAGIC + str(my_ip)

    s.sendto(data.encode(), ('<broadcast>', PORT))
    print('Sent service announcement')

    sleep(1)
    #  s.recvall()
