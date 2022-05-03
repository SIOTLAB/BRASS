#!/usr/bin/python

from cgitb import enable
from distutils.log import error
import re
import time

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
    server_address = (IP, int(PORT))
    print(server_address)
    # I don't understand what is happening here, why do we want to bind this address on controller side?
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
    resReq.id = "resv" + str(currentId)
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
    #print(edges)
    minLink = min(edges, key=lambda e: topology[e[0]][e[1]]["bandwidth"])
    minBandwidth = topology[minLink[0]][minLink[1]]["bandwidth"]
    #print(bandwidth, minBandwidth)
    return bandwidth <= int(minBandwidth)


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
        #print("No path found")
        message = "NO"
        return message
    print("path found:", path)
    for switch in path:
        # Don't send eAPI commands to end hosts -- may be a better way to implement in the future.
        # Currently, this relies on naming convention of switches as sw<num>-<rack>
        if switch.find("sw") == -1:
            continue

        url = "https://{}:{}@{}/command-api".format(
            usernames[switch], passwords[switch], ips[switch]
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
        burst_size = 128 if switch.find('22') == 2 else 256 

        # calculate new remaining bandwidth on the link
        edges = list(zip(path, path[1:]))
        for link in edges:
            if link[0] == switch or link[1] == switch:
                found = link
                break
        #print(link)
        new_remaining = topology[link[0]][link[1]]["bandwidth"] - resReq.bandwidth
        topology[link[0]][link[1]]["bandwidth"] = new_remaining

        resMesg["params"]["cmds"] = [
            "enable",
            "configure",
            f"ip access-list {resReq.id}",
            f"permit tcp {resReq.senderIp}/24 eq {resReq.senderPort} {resReq.destIp}/24 eq {resReq.senderPort}",
            "exit",
            "ip access-list default",
            "permit ip any any",
            "exit",
            f"class-map match-any {resReq.id}",
            f"match ip access-group {resReq.id}",
            "exit",
            f"policy-map {resReq.id}",
            f"class {resReq.id}",
            f"police rate {resReq.bandwidth} bps burst-size {burst_size} mbytes",
            "exit",
            "class default",
            f"police rate {new_remaining} bps burst-size {burst_size} mbytes",
            "exit",
            "exit",
            #"interface ethernet 1/1",
            #f"service-policy input {resReq.id}",
            #"exit",
        ]
        #print(resMesg["params"]["cmds"])
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
        
        response = eapi_conn.runCmds(1, resMesg["params"]["cmds"])[0]
        print(f"Established policy map on switch: {switch}")
        
    edges = list(zip(path, path[1:]))
    #pprint(edges)
    
    for edge in edges:
        sideA, sideB = edge
        # if sideA represents a switch, if its an end host, no reservation to apply.
        if sideA.find("sw") != -1:
            eth = topology[sideA][sideB]["ports"][sideA] 
            url = "https://{}:{}@{}/command-api".format(
                usernames[sideA], passwords[sideA], ips[sideA]
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
                f"service-policy input {resReq.id}"
                "exit"
            ]
            response = eapi_conn.runCmds(1, cmds)[0]
            print(f"Applied policy map to switch: {sideA}, port {eth}")

        # if sideB represents a switch, if its an end host, no reservation to apply.
        if sideB.find("sw") != -1:
            eth = topology[sideA][sideB]["ports"][sideB]
            url = "https://{}:{}@{}/command-api".format(
                usernames[sideB], passwords[sideB], ips[sideB]
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
                f"service-policy input {resReq.id}",
                "exit"
            ]
            response = eapi_conn.runCmds(1, cmds)[0]
            print(f"Applied policy map to switch: {sideB}, port {eth}")

    currentId = resReq.id
    establishedRequests[currentId] = resReq
    message = "YES"

    return message


def consumer(queue, lock):  # Handle queued requests
    # block on empty queue
    print("consumer starting")
    while True:
        item = queue.get()
        with lock:
            resReq = prepareRequest(item)  # Format the request
            message = establishReservation(resReq)
            print(message)
            #errorChecking(resReq, message)
        queue.task_done()


#
## SWITCHING DEVICE HANDLER
#
class SwitchHandler(threading.Thread):  # Communicate with switches
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # was getting an error below, changed to hard coded
        s.bind(("10.16.224.150", 5005))
        s.listen(1)
        print("switch handler listening at 10.16.224.150 on port 5005")
        global BUFFER_SIZE
        global ips
        global topology
        global usernames
        global passwords
        
        # Moved outside of while loop -- for TCP, we establish
        # connection once, and then send multiple messages through it.
        while 1:
            conn, addr = s.accept()
            print("Connection address:", addr)
           
            while 1:
                try:
                    data = conn.recv(BUFFER_SIZE)
                except:
                    break

                if not data:
                    break
                data_str = data.decode()  # received (switch_name, user_name, eapi_password)
                data_str = eval(data_str) # eval converts string -> list
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
                    ips[data_str[0]] = addr[0]
                    usernames[data_str[0]] = data_str[1]
                    passwords[data_str[0]] = data_str[2]
                    #print(ips)
                    #print(usernames)
                    #print(passwords)
                    url = "https://{}:{}@{}/command-api".format(
                        usernames[data_str[0]], passwords[data_str[0]], ips[data_str[0]]
                    )  # url format(username, password, ip)
                    #print(url)
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
                    #print(payload)
                    response = eapi_conn.runCmds(1, payload)[0]
                    neighbors = response["lldpNeighbors"]

                    for n in neighbors:
                        payload[0] = "show interfaces " + n["port"] + " status"
                        response = eapi_conn.runCmds(1, payload)[0]
                        neighbor_name = n["neighborDevice"]
                        
                        print("adding edge: (", data_str[0], ", ", neighbor_name, ")")

                        topology.add_edge(data_str[0], neighbor_name)
                        topology[data_str[0]][neighbor_name]["total_bandwidth"] = response[
                            "interfaceStatuses"
                        ][n["port"]]["bandwidth"]
                        topology[data_str[0]][neighbor_name]["bandwidth"] = topology[data_str[0]][neighbor_name]["total_bandwidth"]

                        topology[data_str[0]][neighbor_name]["ports"] = {}
                        topology[data_str[0]][neighbor_name]["ports"][data_str[0]] = n["port"]
                        topology[data_str[0]][neighbor_name]["ports"][neighbor_name] = n["neighborPort"]

                    #print(ips)
                    #print(topology["sw24-r224"]["sw23-r224"]["ports"])
                    response = "Switch discovered by controller."

                conn.send(str.encode(response))  # echo
            print("Connection with switch ended, listening for next connection")
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
                # Tee second half of the conditional is to ensure we don't add switch management IPs to the 
                # possible paths. There could be a better way to do this in the future.
                if not entry["address"] in ips.values() and entry["address"].find("10.16.224") == -1:
                    topology.add_node(entry["address"])
                    topology.add_edge(entry["address"], switch_name)
                    
                    cmds = [
                        "enable",
                        f"show interfaces {entry['interface']} status"
                    ]
                    response = eapi_conn.runCmds(1, cmds)[1]
                    bandwidth = response['interfaceStatuses'][entry['interface']]['bandwidth']

                    topology[switch_name][entry["address"]]["total_bandwidth"] = bandwidth
                    topology[switch_name][entry["address"]]["bandwidth"] = bandwidth

                    topology[switch_name][entry["address"]]["ports"] = {}
                    topology[switch_name][entry["address"]]["ports"][switch_name] = entry["interface"]
                    topology[switch_name][entry["address"]]["ports"][entry["address"]] = "N/A -- End Host"
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
        data = ReservationRequest(data["src"], data["dest"], int(data["resv"])*1000000, data["dura"], data["src_port"])
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
        global req
        print(req)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        IP = "10.16.224.150"
        PORT = 9434
        server_address = (IP, PORT)
        s.bind(server_address)
        print("Host manager bound on 10.16.224.150 port 9434") 

        #time.sleep(15)
        #queue.put(req)
        #print("put data in queue")
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
data = '{"src": "24.224.1.2", "src_port": "5001", "dest": "22.224.1.2", "resv": 30000, "dura": 5.0, "protocol": "tcp", "dest_port": "5001"}'
req = hm.parseMsg(data, CONTROLLER_IP, CONTROLLER_PORT)
