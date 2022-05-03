#!/usr/bin/python

from cgitb import enable
from distutils.log import error
import re

# from tkinter import Toplevel
from importsAndGlobal import (
    CONTROLLER_IP,
    CONTROLLER_PORT,
    queue,
    establishedRequests,
    threading,
    datetime,
    BUFFER_SIZE,
    msgPrefix,
    svrPrefix,
    ReservationRequest,
    id,
    ips,
    topology,
    usernames,
    passwords,
    resMesg,
)
import json
import jsonrpclib
import ssl
import socket
import trace
import networkx as nx
from pprint import pprint

#
## MAIN THREAD
#   - CORE LOGIC
#

rsrv_success = ["Reservation established"]
rsrv_error = ["Bandwidth not available", "Path does not exist", "Reservation Failed"]


def errorChecking(data, message):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    IP = data.senderIp
    PORT = data.senderPort
    server_address = (IP, PORT)
    s.bind(server_address)

    #   if message starts with YES: the reservation could be instantiated
    if message.startswith("YES"):
        s.sendto((svrPrefix + rsrv_success[0]).encode(), data.address)

    #   if message starts with NO: the reservation could NOT be instantiated
    if message.startswith("NO"):
        s.sendto((svrPrefix + rsrv_error[2]).encode(), data.address)

    #   if message starts with CLOSE: quit the host manager thread(s)
    if message.startswith("CLOSE"):
        # return something to the socket??
        return False

    return True


def prepareRequest(data):
    # Generate an ID for this reservation
    # Return the ID generated and send to the end device
    global id
    data.id = id
    id += 1
    expirationTime = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=data.duration
    )
    data.expirationTime = expirationTime
    return data


def checkPathBandwidth(path, bandwidth):
    # path is a list
    # bandwidth is an attribut of edges
    edges = list(zip(path, path[1:]))
    minBandwidth = min(edges, key=lambda e: topology[e[0]][e[1]]["bandwidth"])
    return bandwidth >= minBandwidth


def getPath(data):  # returns a list of IP addresses of swtiches along route
    paths = list(
        nx.shortest_simple_paths(
            topology, data.senderIp, data.destIp, weight="bandwidth"
        )
    )

    bestPath = None
    for path in paths:
        hasBandwidth = checkPathBandwidth(path, data.bandwidth)
        if hasBandwidth:
            # has enough bandwidth
            bestPath = path
            break

    return bestPath


def establishReservation(
    data
):  # returns whether or not the request was established via a message
    global resMesg
    message = "LOG: "

    path = getPath(data)
    if not (path):
        message = "NO"
        return message

    for switch in path:
        url = "https://{}:{}@{}/command-api".format(
            switch, passwords[switch], ips[switch]
        )

        #   SSL certificate check keeps failing; only use HTTPS verification if possible
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:  #   Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:  #   Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

        eapi_conn = jsonrpclib.Server(url)

        if data.protocl == "tcp":
            resMesg["params"]["cmds"] = [
                "enable",
                "configure",
                "ip access-list acl_rsv_"
                + data.id
                + " permit tcp "
                + data.senderIp
                + " eq "
                + data.senderPort
                + " "
                + data.destIp
                + " eq "
                + data.destPort,
            ]
        elif data.protocl == "udp":
            resMesg["params"]["cmds"] = [
                "enable",
                "configure",
                "ip access-list acl_rsv_"
                + data.id
                + " permit udp "
                + data.senderIp
                + " eq "
                + data.senderPort
                + " "
                + data.destIp
                + " eq "
                + data.destPort,
            ]
        else:
            resMesg["params"]["cmds"] = [
                "enable",
                "configure",
                "ip access-list <name> permit ip <source ip> <dest ip>",
                "ip access-list acl_rsv_"
                + data.id
                + " permit ip "
                + data.senderIp
                + " "
                + data.destIp,
            ]

        # Creating a class map
        # Creating an ACL for that specific source/dest
        # Some other way of distinguising with like a header value?
        # Apply ACL to class map
        # Apply class map to policy map
        payload = [""]
        response = eapi_conn.runCmds(1, payload)[0]
        neighbors = response["lldpNeighbors"]

    currentId = data.id
    establishedRequests[currentId] = data
    message = "YES"

    return message


def consumer(queue, lock):  # Handle queued requests
    # block on empty queue

    while True:
        item = queue.get()
        with lock:
            data = prepareRequest(item)  # Format the request
            message = establishReservation(data)
            errorChecking(data, message)
        queue.task_done()


#
## SWITCHING DEVICE HANDLER
#
class SwitchHandler(threading.Thread):  # Communicate with switches
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)
        global BUFFER_SIZE
        global ips
        global topology
        global usernames
        global passwords

        while 1:
            conn, addr = s.accept()
            print("Connection address:", addr)

            try:
                data = conn.recv(BUFFER_SIZE)
            except:
                break

            if not data:
                break
            data_str = data.decode()  # received (switch_name, user_name, eapi_password)

            # Could receive two types of messages 1) and ARP table update message, or 2) a new switch discovery message.
            if data_str[1] == "ARP":
                print("Received ARP update message from", data_str[0])
                if self.fetchArpTable(data_str[0]):
                    response = "Sucessful ARP update."
                else:
                    response = "Failed ARP update."
            else:
                print("Received switch information from", data_str[0])
                ips[data_str[0]] = addr[0]
                usernames[data_str[0]] = data_str[1]
                passwords[data_str[0]] = data_str[2]
                url = "https://{}:{}@{}/command-api".format(
                    data_str[1], data_str[2], addr[0]
                )  # url format(username, password, ip)

                #   Add the switch to the topology
                topology.add_node(data_str[0])  # add the switch to the graph by name

                #   SSL certificate check keeps failing; only use HTTPS verification if possible
                try:
                    _create_unverified_https_context = ssl._create_unverified_context
                except AttributeError:  #   Legacy Python that doesn't verify HTTPS certificates by default
                    pass
                else:  #   Handle target environment that doesn't support HTTPS verification
                    ssl._create_default_https_context = _create_unverified_https_context

                eapi_conn = jsonrpclib.Server(url)

                payload = ["show lldp neighbors"]
                response = eapi_conn.runCmds(1, payload)[0]
                neighbors = response["lldpNeighbors"]

                for n in neighbors:
                    payload[0] = "show interfaces " + n["port"] + " status"
                    response = eapi_conn.runCmds(1, payload)[0]
                    neighbor_name = n["neighborDevice"]

                    topology.add_edge(data_str[0], neighbor_name)
                    topology[data_str[0]][neighbor_name]["total_bandwidth"] = response[
                        "interfaceStatuses"
                    ][n["port"]]["bandwidth"]

                print(ips)
                response = "Switch discovered by controller."

            conn.send(response)  # echo
        conn.close()

    def fetchArpTable(self, switch_name):
        url = "https://{}:{}@{}/command-api".format(
            usernames[switch_name], passwords[switch_name], ips[switch_name]
        )  # format(username, password, ip)
        #   SSL certificate check keeps failing; only use HTTPS verification if possible
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:  # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:  # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

        eapi_conn = jsonrpclib.Server(url)

        payload = ["show arp"]
        try:
            response = eapi_conn.runCmds(1, payload)[0]
            arpTable = response["ipV4Neighbors"]

            for entry in arpTable:
                if not entry["address"] in ips.values():
                    topology.add_node(entry["address"])
                    topology.add_edge(entry["address"], switch_name)
            return True
        except:
            return False


#
## END DEVICE HANDLER
#
class HostManager(threading.Thread):  # Communicate with hosts
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def parseMsg(self, data):
        data = json.loads(data)  # Host info stored in dict
        data = ReservationRequest(
            data["src"],
            data["src_port"],
            data["dest"],
            data["dest_port"],
            data["resv"],
            data["dura"],
            data["protocol"],
        )
        return data

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        IP = "10.16.224.150"
        PORT = 9434
        server_address = (IP, PORT)
        s.bind(server_address)

        while True:
            data, address = s.recvfrom(4096)
            data = str(data.decode())

            if data.startswith(msgPrefix):
                data = self.parseMsg(data[len(msgPrefix) :])
                queue.put(data)  # Push reservation request to queue

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == "line":
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


# TEST 1
#   Reservation messages received from hosts are formated as follows in 'data', and parseMsg() should return a correctly configured ReservationRequest object.
hm = HostManager()
data = '{"src": "10.16.224.24", "src_port": "5000", "dest": "10.16.224.22", "resv": 10, "dura": 5.0, "protocol": "tcp", "dest_port": "5000"}'
data = hm.parseMsg(data)
data = prepareRequest(data)
print(
    "ip access-list acl_rsv_"
    + str(data.id)
    + " permit udp "
    + data.senderIp
    + " eq "
    + data.senderPort
    + " "
    + data.destIp
    + " eq "
    + data.destPort
)
