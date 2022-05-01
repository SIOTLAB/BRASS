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


def errorChecking(resReq, message):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    IP = resReq.senderIp
    PORT = resReq.senderPort
    server_address = (IP, PORT)
    s.bind(server_address)

    #   if message starts with YES: the reservation could be instantiated
    if message.startswith("YES"):
        s.sendto((svrPrefix + rsrv_success[0]).encode(), resReq.address)

    #   if message starts with NO: the reservation could NOT be instantiated
    if message.startswith("NO"):
        s.sendto((svrPrefix + rsrv_error[2]).encode(), resReq.address)

    #   if message starts with CLOSE: quit the host manager thread(s)
    if message.startswith("CLOSE"):
        # return something to the socket??
        return False

    return True


def prepareRequest(resReq):
    # generate an ID for this reservation
    # return the ID generated and send to the end device
    global id
    currentId = id
    id += 1
    resReq.id = currentId
    expirationTime = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=resReq.duration
    )
    resReq.expirationTime = expirationTime

    pprint(vars(resReq))
    return resReq


def checkPathBandwidth(path, bandwidth):
    # path is a list
    # bandwidth is an attribut of edges
    edges = list(zip(path, path[1:]))
    minBandwidth = min(edges, key=lambda e: topology[e[0]][e[1]]["bandwidth"])
    return bandwidth >= minBandwidth


def getPath(resReq):  # returns a list of IP addresses of swtiches along route
    paths = list(
        nx.shortest_simple_paths(
            topology, resReq.senderIp, resReq.destIp, weight="bandwidth"
        )
    )

    bestPath = None
    for path in paths:
        hasBandwidth = checkPathBandwidth(path, resReq.bandwidth)
        if hasBandwidth:
            # has enough bandwidth
            bestPath = path
            break

    return bestPath


def establishReservation(
    resReq
):  # returns whether or not the request was established via a message
    global resMesg
    message = "LOG: "

    path = getPath(resReq)
    if not (path):
        message = "NO"
        return message
    pprint(path)
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

        resMesg["params"]["cmds"] = [
            "enable",
            "configure",
            "ip access-list <name> permit udp <source ip> eq <source port> <dest ip> eq <dest port>",
        ]
        # "ip access-list <name> permit tcp <source ip> eq <source port> <dest ip> eq <dest port>"
        # "ip access-list <name> permit ip <source ip> <dest ip>"
        
        # Creating a class map
        # Creating an ACL for that specific source/dest
        # Some other way of distinguising with like a header value?
        # Apply ACL to class map
        # Apply class map to policy map

        # SET OF WORKING COMMANDS TO CREATE ACL test1, CREATE class-map test1, 
        # CREATE policy-map test1, set policers for pmap, and apply to interface 1/1

        # enable
        # configure
        # ip access-list test1
        # permit tcp 24.224.1.0/24 eq 5001 22.224.1.0/24 eq 5001
        # exit
        # class-map match-any test1
        # match ip access-group test1
        # exit
        # policy-map test1
        # class test1
        # police rate 30000 mbps burst-size 256 mbytes
        # exit
        # class default
        # police rate 10000 mbps burst-size 256 mbytes
        # exit
        # exit
        # interface ethernet 1/1
        # service-policy input test1
        
        payload = [""]
        response = eapi_conn.runCmds(1, payload)[0]
        neighbors = response["lldpNeighbors"]

    currentId = resReq.id
    establishedRequests[currentId] = resReq
    message = "YES"

    return message


def consumer(queue, lock):  # Handle queued requests
    # block on empty queue

    while True:
        item = queue.get()
        with lock:
            resReq = prepareRequest(item)  # Format the request
            message = establishReservation(resReq)
            errorChecking(resReq, message)
        queue.task_done()


#
## SWITCHING DEVICE HANDLER
#
class SwitchHandler(threading.Thread):  # Communicate with switches
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        global TCP_IP
        global TCP_PORT
        s.bind(("10.16.224.150", 5005))
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
                                      # Where is this supposed to come from ^^? Not being sent correctly.
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
                print(usernames)
                print(passwords)
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
                print(payload)
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
                    topology[data_str[0]][neightbor_name]["ethA"] = n["port"]
                    topology[data_str[0]][neightbor_name]["ethB"] = n["neighborPort"]

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

    def parseMsg(self, data, ip, port):
        print(data)
        data = json.loads(data)  # Host info stored in dict
        # data = json.loads(data.decode("UTF-8"))  # Host info stored in dict
        data = ReservationRequest(data["src"], data["dest"], data["resv"], data["dura"], data["src_port"])
        print(data)
        # ReservationRequest(senderIp, destIp, bandwidth, duration, port)
        #         self.senderIp = senderIp
        #         self.destIp = destIp
        #         self.bandwidth = bandwidth
        #         self.duration = (
        #             duration
        #         )  # duration is measured from when the request is established on the controller, scale is in seconds
        #         self.senderPort = port
        #         self.expirationTime = None
        #         self.id = None  # id is added when reservation is established
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
                data = self.parseMsg(data[len(msgPrefix) :], IP, PORT)
                queue.put(data)  # Push reservation request to queue

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == "line":
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


hm = HostManager()
data = "{\"src\": \"10.16.224.24\", \"src_port\": \"5000\", \"dest\": \"10.16.224.22\", \"resv\": 10, \"dura\": 5.0, \"protocol\": \"tcp\", \"dest_port\": \"5000\"}"
hm.parseMsg(data, CONTROLLER_IP, CONTROLLER_PORT)
