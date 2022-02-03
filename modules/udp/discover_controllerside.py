#!/usr/bin/env python

import os
import socket
import threading

#  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SOCK = socket.socket()
#  IP = '10.16.252.10'
IP = "127.0.0.1"
PORT = 9434
MESSAGE = "pfg_ip_response_serv"
RESPONSE = "pfg_ip_broadcast_cl"

threadCount = 0

try:
    SOCK.bind((IP, PORT))
except socket.error as e:
    print(str(e))
print("Server bound on " + IP + ":" + str(PORT))

print("Waiting for a connection...")
SOCK.listen(5)


def threaded_client(connection, address):
    connection.send(str.encode("Welcome to the server"))
    while True:
        data = connection.recv(2048)
        #  data, address = sock.recvfrom(4096)
        reply = str(data.decode("utf-8"))
        print("From " + str(address[1]) + ": " + reply)

        if not data:
            break

        connection.sendall(str.encode(reply))

    connection.close()

    #  if data == RESPONSE:
    #      sent = sock.sendto(MESSAGE.encode(), address)
    #  print(address[0])


while True:
    client, address = SOCK.accept()
    print("Connected to: " + address[0] + ":" + str(address[1]))

    thread = threading.Thread(target=threaded_client, args=(client, address, ))
    thread.start()
    threadCount += 1
    print("Thread number: " + str(threadCount))

    thread.join()
    threadCount -= 1
    print("Thread number: " + str(threadCount))

SOCK.close()
