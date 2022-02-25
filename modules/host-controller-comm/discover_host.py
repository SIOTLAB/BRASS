#!/usr/bin/env python

import argparse
import json
from socket import *
import sys
import time


def duration_type(x):
    x = float(x)
    if x > 3600:
        raise argparse.ArgumentTypeError("Maximum duration is 1 hour")
    return x


# PARSE ARGUMENTS
parser = argparse.ArgumentParser(
    description="Request an amount of reservation from a network controller."
)
parser.add_argument(
    "dest",
    metavar="A.B.C.D",
    type=str,
    help="destination IP for reserved communication",
)
parser.add_argument(
    "resv", metavar="KB", type=int, help="amount of bandwidth reservation in KiloBytes"
)
parser.add_argument(
    "dura", metavar="sec", type=duration_type, help="duration of reservation in seconds"
)

args = parser.parse_args()
message = json.dumps(vars(args))  # JSON FORMATTED ARGUMENTS

# CREATE UDP SOCKET
sock = socket(AF_INET, SOCK_DGRAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
sock.settimeout(5)

IP = "10.16.224.150"
PORT = 9434
server_address = (IP, PORT)
msgPrefix = "pfg_ip_broadcast_cl"
svrPrefix = "pfg_ip_response_serv"

timeout_count = 0
try:
    while True:
        # SEND DATA
        print("sending: " + message)
        sent = sock.sendto((msgPrefix + message).encode(), server_address)

        # RECEIVE RESPONSE
        try:
            print("waiting for response")
            data, server = sock.recvfrom(4096)
            if data.decode("UTF-8").startswith(svrPrefix):
                print("received: " + data[len(svrPrefix):])
                print("server ip: " + str(server[0]))
                break
            else:
                print("verification failed\n")
        except timeout:
            timeout_count += 1
            print("\ttimeout " + str(timeout_count))
            if timeout_count == 5:
                break
            else:
                print("\ttrying again...")
            print("")


finally:
    sock.close()
