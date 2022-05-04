#!/usr/bin/python3

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


def protocol_type(x):
    x = x.lower()
    if x not in ["udp", "tcp"]:
        raise argparse.ArgumentTypeError("Unsupported protocol")
    return x


# PARSE ARGUMENTS
parser = argparse.ArgumentParser(
    description="Request an amount of reservation from a network controller."
)
parser.add_argument("control_ip", metavar="A.B.C.D", type=str, help="controller IP.")
parser.add_argument("control_port", metavar="C_Port", type=str, help="controller Port.")
parser.add_argument("src", metavar="E.F.G.H", type=str, help="source device IP.")
parser.add_argument("src_port", metavar="S_Port", type=str, help="source device Port.")
parser.add_argument(
    "dest_ip", metavar="I.J.K.L", type=str, help="destination device IP."
)
parser.add_argument(
    "dest_port", metavar="D_Port", type=str, help="destination device Port."
)
parser.add_argument(
    "resv", metavar="KB", type=int, help="Reservation bandwidth in kilobytes."
)
parser.add_argument(
    "dura", metavar="sec", type=duration_type, help="Reservation duration in seconds."
)
parser.add_argument(
    "protocol", type=protocol_type, help="Traffic flow protocol: TPC, UDP, or IP."
)

args = vars(parser.parse_args())
controller_ip = args.pop("control_ip")
controller_port = args.pop("control_port")
message = json.dumps(args)  # JSON FORMATTED ARGUMENTS

# CREATE UDP SOCKET
sock = socket(AF_INET, SOCK_DGRAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
sock.settimeout(5)

server_address = (controller_ip, controller_port)
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
                print("received: " + data[len(svrPrefix) :])
                print("server ip: " + str(server[0]))
                break
            else:
                print("verification failed\n")
        except timeout:
            timeout_count += 1
            print("\ttimeout " + str(timeout_count))
            if timeout_count == 1:
                break
            else:
                print("\ttrying again...")
            print("")

finally:
    sock.close()
