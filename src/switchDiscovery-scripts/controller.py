#!/usr/bin/env python
# Test script for recieving switch hellos on controller end. This script is no longer needed for 
# host discovery and functionaly has been merged into main controller process.
import socket


TCP_IP = '10.16.252.10'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print('Connection address:', addr)
while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data:
        break
    print("received data:", data)
    conn.send(data)  # echo
conn.close()
