#!/usr/bin/python

from distutils.log import error
from tkinter import Toplevel
from importsAndGlobal import queue, establishedRequests, threading, datetime, TCP_IP, TCP_PORT, BUFFER_SIZE, msgPrefix, svrPrefix, ReservationRequest, id, ips, topology
import json
import socket
import trace
import networkx as nx
from pprint import pprint

#
## MAIN THREAD
#   - CORE LOGIC
#

rsrv_success = [
    "Reservation established"
]
rsrv_error = [
    "Bandwidth not available",
    "Path does not exist",
    "Reservation Failed"
]

def getMessage(resReq):
    return "YES wow it works so cool"

def errorChecking(resReq, message):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    IP = resReq.ip
    PORT = resReq.port
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
    expirationTime = datetime.datetime.utcnow() + datetime.timedelta(minutes=resReq.duration)
    resReq.expirationTime = expirationTime

    pprint(vars(resReq))

    return resReq

def establishReservation(resReq): # returns whether or not the request was established via a message
    message = "CLOSE"   # reservation could be instantiated

    # TODO
    # if(there is enough bandwidth for the request):
    #       Check NetworkX
    # labels = nx.get_edge_attributes(G, "bandwidth")
    # pls = nx.spring_layout(G)
    # nx.draw_networkx(G, pls)
    # nx.draw_networkx_edge_labels(G, pls, labels)

    if(True):
        currentId = resReq.id
        establishedRequests[currentId] = resReq
        message = "YES"
    else:
        # reservation could not be instantiated
        message = "NO"
    # if message starts with CLOSE: quit the host manager thread(s)
    return message

def consumer(queue, lock):   # Handle queued requests
    # block on empty queue

    while True:
        item = queue.get()
        with lock:
            resReq = prepareRequest(item)
            message = establishReservation(resReq)
            errorChecking(resReq, message)
        queue.task_done()

#
## SWITCHING DEVICE HANDLER
#
class SwitchHandler(threading.Thread): # Communicate with switches
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)

        while 1:
            conn, addr = s.accept()
            print('Connection address:', addr)
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            data_str = data.decode()
            #   TODO: The data_str should contain be a tuple of (switch_name, eapi_username, eapi_password)
            print("received data:", data_str)
            ips[data_str] = addr[0]

            #   Add the switch to the topology
            # topology.add_node(data_str[0])

            # url = 'https://{}:{}@{}/command-api'.format(data_str[1], data_str[2], addr[0])

            #   SSL certificate check keeps failing; only use HTTPS verification if possible
            # try:
            #     _create_unverified_https_context = ssl._create_unverified_context
            # except AttributeError:  #   Legacy Python that doesn't verify HTTPS certificates by default
            #     pass
            # else:                   #   Handle target environment that doesn't support HTTPS verification
            #     ssl._create_default_https_context = _create_unverified_https_context

            # eapi_conn = jsonrpclib.Server(url)

            # payload = ["show lldp neighbors"]
            # response = eapi_conn.runCmds(1, payload)[0]

            # neighbors = response['lldpNeighbors']

            # topology.add_edge(name, neighbor_name)
            # bandwidth = response['interfaceStatuses'][n['port']]['bandwidth']
            # topology[name][neighbor_name]['bandwidth'] = bandwidth

            #   TODO: receive and handle ARP table of end hosts
            print(ips)
            conn.send(data)  # echo
        conn.close()

#
## END DEVICE HANDLER
#
class HostManager(threading.Thread):    # Communicate with hosts
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        IP = '10.16.224.150'
        PORT = 9434
        server_address = (IP, PORT)
        s.bind(server_address)
        
        while True:
            data, address = s.recvfrom(4096)
            data = str(data.decode())

            if data.startswith(msgPrefix):
                data = data[len(msgPrefix):]
                data = json.loads(data.decode('UTF-8')) # Host info stored in dict
                data = ReservationRequest(*data, IP, PORT)
                queue.put(data)  # Push reservation request to queue
    
    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace
    
    def kill(self):
        self.killed = True