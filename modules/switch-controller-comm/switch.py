#!/usr/bin/env python

import argparse
import json
import socket
import os

USER = os.getenv("USER")
TCP_PORT = 5005
BUFFER_SIZE = 1024

parser = argparse.ArgumentParser(
    description="Connect to a reservation request handler controller. (SD-TCA)"
)
parser.add_argument(
    "controllerIP", metavar="A.B.C.D", type=str, help="Controller IP address."
)
parser.add_argument(
    "controllerPort", metavar="Port", type=str, help="Controller port number."
)
parser.add_argument("password", type=str, help="eAPI server password.")

args = parser.parse_args()
args = json.dumps(vars(args))  #    JSON FORMATTED ARGUMENTS

msg_prefix = "pfg_ip_broadcast_cl"
svr_prefix = "pfg_ip_response_serv"
switch_name = socket.gethostname()
tcp_ip = args["controller"]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((tcp_ip, TCP_PORT))

#   SEND SWITCH DISCOVERY INFORMATION
message = [switch_name, USER, args["password"]]
s.send(str.encode(message))
data = s.recv(BUFFER_SIZE)

#   SEND SWITCH ARP INFO
# if argTable is updated:
message = [switch_name, "ARP"]
s.send(str.encode(message))
data = s.recv(BUFFER_SIZE)

s.close()
print("received data:", data)
