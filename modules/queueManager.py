#!/usr/bin/python

from distutils.log import error
from importsAndGlobal import queue, establishedRequests, threading, datetime, TCP_IP, TCP_PORT, BUFFER_SIZE, msgPrefix, svrPrefix, ReservationRequest, id
import json
import socket
from pprint import pprint

class Discoverer(threading.Thread): # Communicate with switches
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)

        conn, addr = s.accept()
        print('Connection address:', addr)
        while 1:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            data_str = data.decode()
            print("received data:", data_str)
            conn.send(data)  # echo
        conn.close()

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

def errorChecking(resReq):

    message = getMessage(resReq)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    IP = '10.16.224.150'
    PORT = 9434
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
        # return somethign to the socket??
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

def establishReservation(resReq):
    currentId = resReq.id
    
    # do whatever it takes to establish the reservation with other devices

    establishedRequests[currentId] = resReq
    return currentId

def consumer(queue, lock):   # Handle queued requests
    # block on empty queue

    while True:
        item = queue.get()
        with lock:            
            #if (errorChecking(item)):
            if (True):
                resReq = prepareRequest(item)
                establishReservation(resReq)
        queue.task_done()

class HostManager(threading.Thread):
 
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
                data = ReservationRequest(*data, s, address)
                queue.put(data)  # Push reservation request to queue
