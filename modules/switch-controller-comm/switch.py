#!/usr/bin/env python

import argparse
import json
import socket

TCP_IP = '10.16.224.22'
TCP_PORT = 5005
BUFFER_SIZE = 1024

parser = argparse.ArgumentParser(
    description="Connect to a reservation request handler controller. (SD-TCA)")
parser.add_argument("controller",
                    metavar="A.B.C.D",
                    type=str,
                    help="Controller IP address.")
parser.add_argument("password",
                    type=str,
                    help="eAPI server password.")

args = parser.parse_args()
args = json.dumps(vars(args))  # JSON FORMATTED ARGUMENTS

msgPrefix = 'pfg_ip_broadcast_cl'
svrPrefix = 'pfg_ip_response_serv'
message = [socket.gethostname(), args['password']]
# TODO: Send ARP info too.

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(str.encode(message))
data = s.recv(BUFFER_SIZE)

# TODO: Wait for a response.
s.close()

print("received data:", data)
