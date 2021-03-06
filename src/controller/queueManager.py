#!/usr/bin/python

from cgitb import enable
from distutils.log import error
import re
import time

# from tkinter import Toplevel
import datetime
import threading
import queue
import importsAndGlobal as glob
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

    IP = data.callbackIp
    PORT = data.callbackPort
    host_address = (IP, int(PORT))
    # IP = resReq.senderIp
    # PORT = resReq.senderPort
    # server_address = (IP, int(PORT))
    # print(server_address)
    # I don't understand what is happening here, why do we want to bind this address on controller side?
    # s.bind(server_address)
    print(f"reservation established? : {message}")
    #   if message starts with YES: the reservation could be instantiated
    if message.startswith("YES"):
        s.sendto((glob.svrPrefix + rsrv_success[0]).encode(), host_address)

    #   if message starts with NO: the reservation could NOT be instantiated
    if message.startswith("NO"):
        s.sendto((glob.svrPrefix + rsrv_error[2]).encode(), host_address)

    #   if message starts with CLOSE: quit the host manager thread(s)
    if message.startswith("CLOSE"):
        # return something to the socket??
        return False

    return True


def prepareRequest(data):
    # Generate an ID for this reservation
    # Return the ID generated and send to the end device

    data.id = glob.id
    glob.id += 1
    data.id = "resv" + str(data.id)
    expirationTime = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=data.duration
    )
    data.expirationTime = expirationTime
    return data


def checkPathBandwidth(path, bandwidth):
    # path is a list
    # bandwidth is an attribut of edges
    edges = list(zip(path, path[1:]))
    # print(edges)
    minLink = min(edges, key=lambda e: glob.topology[e[0]][e[1]]["bandwidth"])
    minBandwidth = glob.topology[minLink[0]][minLink[1]]["bandwidth"]
    # print(bandwidth, minBandwidth)
    return bandwidth <= int(minBandwidth)


def getPath(data):  # returns a list of IP addresses of swtiches along route
    paths = list(
        nx.shortest_simple_paths(
            glob.topology, data.senderIp, data.destIp, weight="bandwidth"
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
        # print("No path found")
        message = "NO"
        return message
    print("path found:", path)
    for switch in path:
        # Don't send eAPI commands to end hosts -- may be a better way to implement in the future.
        # Currently, this relies on naming convention of switches as sw<num>-<rack>
        if switch.find("sw") == -1:
            continue

        url = "https://{}:{}@{}/command-api".format(
            glob.usernames[switch], glob.passwords[switch], glob.ips[switch]
        )

        #   SSL certificate check keeps failing; only use HTTPS verification if possible
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:  #   Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:  #   Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

        eapi_conn = jsonrpclib.Server(url)
        # switch 22 has maximum burst size of 128 for some reason, while rest have 256. I have no idea why haha.
        burst_size = 128 if switch.find("22") == 2 else 256

        # calculate new remaining bandwidth on the link
        edges = list(zip(path, path[1:]))
        for link in edges:
            if link[0] == switch or link[1] == switch:
                found = link
                break
        # print(link)
        new_remaining = glob.topology[link[0]][link[1]]["bandwidth"] - data.bandwidth
        glob.topology[link[0]][link[1]]["bandwidth"] = new_remaining

        cmds = [
            "enable",
            "configure",
            f"ip access-list {data.id}",
            f"permit tcp {data.senderIp}/24 eq {data.senderPort} {data.destIp}/24 eq {data.senderPort}",
            "exit",
            "ip access-list default",
            "permit ip any any",
            "exit",
            f"class-map match-any {data.id}",
            f"match ip access-group {data.id}",
            "exit",
            f"policy-map {data.id}",
            f"class {data.id}",
            f"police rate {data.bandwidth} bps burst-size {burst_size} mbytes",
            "exit",
            "class default",
            f"police rate {new_remaining} bps burst-size {burst_size} mbytes",
            "exit",
            "exit",
            # "interface ethernet 1/1",
            # f"service-policy input {data.id}",
            # "exit",
        ]
        # print(resMesg["params"]["cmds"])
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

        response = eapi_conn.runCmds(1, cmds)[0]
        print(f"Established policy map on switch: {switch}")

    edges = list(zip(path, path[1:]))
    # pprint(edges)

    for edge in edges:
        sideA, sideB = edge
        # if sideA represents a switch, if its an end host, no reservation to apply.
        if sideA.find("sw") != -1:
            eth = glob.topology[sideA][sideB]["ports"][sideA]
            url = "https://{}:{}@{}/command-api".format(
                glob.usernames[sideA], glob.passwords[sideA], glob.ips[sideA]
            )
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:  #   Legacy Python that doesn't verify HTTPS certificates by default
                pass
            else:  #   Handle target environment that doesn't support HTTPS verification
                ssl._create_default_https_context = _create_unverified_https_context

            eapi_conn = jsonrpclib.Server(url)
            cmds = [
                "enable",
                "configure",
                f"interface {eth}",
                f"service-policy input {data.id}",
                "exit",
            ]
            response = eapi_conn.runCmds(1, cmds)[0]
            print(f"Applied policy map to switch: {sideA}, port {eth}")

        # if sideB represents a switch, if its an end host, no reservation to apply.
        if sideB.find("sw") != -1:
            eth = glob.topology[sideA][sideB]["ports"][sideB]
            url = "https://{}:{}@{}/command-api".format(
                glob.usernames[sideB], glob.passwords[sideB], glob.ips[sideB]
            )
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:  #   Legacy Python that doesn't verify HTTPS certificates by default
                pass
            else:  #   Handle target environment that doesn't support HTTPS verification
                ssl._create_default_https_context = _create_unverified_https_context

            eapi_conn = jsonrpclib.Server(url)
            cmds = [
                "enable",
                "configure",
                f"interface {eth}",
                f"service-policy input {data.id}",
                "exit",
            ]
            response = eapi_conn.runCmds(1, cmds)[0]
            print(f"Applied policy map to switch: {sideB}, port {eth}")

    currentId = data.id
    glob.establishedRequests[currentId] = data
    message = "YES"

    return message


def consumer(queue, lock):  # Handle queued requests
    # block on empty queue
    print("consumer starting")
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
        s.bind((glob.CONTROLLER_IP, glob.CONTROLLER_PORT))
        # was getting an error below, changed to hard coded
        # s.bind(("10.16.224.150", 5005))
        s.listen(1)
        print("switch handler listening at 10.16.224.150 on port 5005")
        # global BUFFER_SIZE
        # global ips
        # global glob.topology
        # global usernames
        # global passwords

        # Moved outside of while loop -- for TCP, we establish
        # connection once, and then send multiple messages through it.
        while 1:
            conn, addr = s.accept()
            print("Connection address:", addr)

            while 1:
                try:
                    data = conn.recv(glob.BUFFER_SIZE)
                except:
                    break

                if not data:
                    break
                data_str = (
                    data.decode()
                )  # received (switch_name, user_name, eapi_password)
                data_str = eval(data_str)  # eval converts string -> list
                # Could receive two types of messages 1) and ARP table update message, or 2) a new switch discovery message.
                print(data_str)
                if data_str[1] == "ARP":
                    print("Received ARP update message from", data_str[0])
                    if self.fetchArpTable(data_str[0]):
                        response = "Sucessful ARP update."
                    else:
                        response = "Failed ARP update."
                else:
                    print("Received switch information from", data_str)
                    glob.ips[data_str[0]] = addr[0]
                    glob.usernames[data_str[0]] = data_str[1]
                    glob.passwords[data_str[0]] = data_str[2]
                    # print(glob.ips)
                    # print(glob.usernames)
                    # print(glob.passwords)
                    url = "https://{}:{}@{}/command-api".format(
                        glob.usernames[data_str[0]],
                        glob.passwords[data_str[0]],
                        glob.ips[data_str[0]],
                    )  # url format(username, password, ip)
                    # print(url)
                    #   Add the switch to the topology
                    glob.topology.add_node(
                        data_str[0]
                    )  # add the switch to the graph by name

                    #   SSL certificate check keeps failing; only use HTTPS verification if possible
                    try:
                        _create_unverified_https_context = (
                            ssl._create_unverified_context
                        )
                    except AttributeError:  #   Legacy Python that doesn't verify HTTPS certificates by default
                        pass
                    else:  #   Handle target environment that doesn't support HTTPS verification
                        ssl._create_default_https_context = (
                            _create_unverified_https_context
                        )

                    eapi_conn = jsonrpclib.Server(url)

                    payload = ["show lldp neighbors"]
                    # print(payload)
                    response = eapi_conn.runCmds(1, payload)[0]
                    neighbors = response["lldpNeighbors"]

                    for n in neighbors:
                        payload[0] = "show interfaces " + n["port"] + " status"
                        response = eapi_conn.runCmds(1, payload)[0]
                        neighbor_name = n["neighborDevice"]

                        print("adding edge: (", data_str[0], ", ", neighbor_name, ")")

                        glob.topology.add_edge(data_str[0], neighbor_name)
                        glob.topology[data_str[0]][neighbor_name][
                            "total_bandwidth"
                        ] = response["interfaceStatuses"][n["port"]]["bandwidth"]
                        glob.topology[data_str[0]][neighbor_name][
                            "bandwidth"
                        ] = glob.topology[data_str[0]][neighbor_name]["total_bandwidth"]

                        glob.topology[data_str[0]][neighbor_name]["ports"] = {}
                        glob.topology[data_str[0]][neighbor_name]["ports"][
                            data_str[0]
                        ] = n["port"]
                        glob.topology[data_str[0]][neighbor_name]["ports"][
                            neighbor_name
                        ] = n["neighborPort"]

                    response = "Switch discovered by controller."

                conn.send(str.encode(response))  # echo
            print("Connection with switch ended, listening for next connection")
            conn.close()

    def fetchArpTable(self, switch_name):
        url = "https://{}:{}@{}/command-api".format(
            glob.usernames[switch_name],
            glob.passwords[switch_name],
            glob.ips[switch_name],
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
                # Tee second half of the conditional is to ensure we don't add switch management IPs to the
                # possible paths. There could be a better way to do this in the future.
                if (
                    not entry["address"] in glob.ips.values()
                    and entry["address"].find("10.16.224") == -1
                ):
                    glob.topology.add_node(entry["address"])
                    glob.topology.add_edge(entry["address"], switch_name)

                    cmds = ["enable", f"show interfaces {entry['interface']} status"]
                    response = eapi_conn.runCmds(1, cmds)[1]
                    bandwidth = response["interfaceStatuses"][entry["interface"]][
                        "bandwidth"
                    ]

                    glob.topology[switch_name][entry["address"]][
                        "total_bandwidth"
                    ] = bandwidth
                    glob.topology[switch_name][entry["address"]][
                        "bandwidth"
                    ] = bandwidth

                    glob.topology[switch_name][entry["address"]]["ports"] = {}
                    glob.topology[switch_name][entry["address"]]["ports"][
                        switch_name
                    ] = entry["interface"]
                    glob.topology[switch_name][entry["address"]]["ports"][
                        entry["address"]
                    ] = "N/A -- End Host"
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
        data = glob.ReservationRequest(
            data["src_ip"],
            data["src_port"],
            data["dest_ip"],
            data["dest_port"],
            int(data["resv"]) * 1000000,
            data["dura"],
            data["protocol"],
            data["callback_ip"],
            data["callback_port"],
        )
        return data

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        server_address = (glob.CONTROLLER_IP, glob.CONTROLLER_PORT + 1)
        s.bind(server_address)
        print(
            f"Host manager bound on {glob.CONTROLLER_IP} port {glob.CONTROLLER_PORT+1}"
        )

        while True:
            data, address = s.recvfrom(4096)
            data = str(data.decode())
            data = json.loads(data[len(glob.msgPrefix) :])
            data["callback_ip"] = address[0]
            data["callback_port"] = address[1]

            data = glob.msgPrefix + json.dumps(data)
            if data.startswith(glob.msgPrefix):
                data = self.parseMsg(data[len(glob.msgPrefix) :])
                glob.queue.put(data)  # Push reservation request to queue

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
data = '{"src_ip": "10.16.224.24", "src_port": "5000", "dest_ip": "10.16.224.22", "resv": 10, "dura": 5.0, "protocol": "tcp", "dest_port": "5000", "callback_ip": "1.1.1.1", "callback_port": 4567}'
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
