#!/usr/bin/python

from importsAndGlobal import CAPACITY, buffer, in_index, out_index, queue, mutex, empty, full, establishReservation, threading, TCP_IP, TCP_PORT, BUFFER_SIZE, ips
import json
import socket
import time

class Discoverer(threading.Thread): # Communicate with switches
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
            print("received data:", data_str)
            ips[data_str] = addr[0]
            print(ips)
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

class HostManager(threading.Thread):
    condition = threading.Condition()
    message = ""

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        IP = '10.16.224.150'
        PORT = 9434
        server_address = (IP, PORT)
        s.bind(server_address)
        msgPrefix = 'pfg_ip_broadcast_cl'
        svrPrefix = 'pfg_ip_response_serv'

        while True:
            data, address = s.recvfrom(4096)
            data = str(data.decode())
            
            if data.startswith(msgPrefix):
                data = data[len(msgPrefix):]
                data = json.loads(data.decode('UTF-8')) # Host info stored in dict
                queue.append(data)  # Push reservation request to queue

                # Wait for response from main thread:
                self.condition.wait()
                #   >> main thread should call HostManager.condition.notify()

                #   if message starts with YES: the reservation could be instantiated
                if self.message.startswith("YES"):
                    s.sendto((svrPrefix + rsrv_success[0]).encode(), address)

                #   if message starts with NO: the reservation could NOT be instantiated
                if self.message.startswith("NO"):
                    s.sendto((svrPrefix + rsrv_error[2]).encode(), address)

                #   if message starts with CLOSE: quit the host manager thread(s)
                if self.message.startswith("CLOSE"):
                    break

class Producer(threading.Thread):   # For testing?
    def run(self):
    
        global CAPACITY, buffer, in_index, out_index, queue
        global mutex, empty, full
    
        itemsInQueue = len(queue)
        
        while itemsInQueue > 0:
            empty.acquire()
            mutex.acquire()
            nextItem = queue.pop()
            buffer[in_index] = nextItem
            in_index = (in_index + 1) % CAPACITY
            
            mutex.release()
            full.release()
            
            time.sleep(1)
            
            itemsInQueue = len(queue)

class Consumer(threading.Thread):   # Handle queued requests
    def run(self):
    
        global CAPACITY, buffer, in_index, out_index, queue
        global mutex, empty, full
    
        itemsInQueue = len(queue)
        while itemsInQueue > 0:
            full.acquire()
            mutex.acquire()
        
            item = buffer[out_index]
            out_index = (out_index + 1) % CAPACITY

            establishReservation(item)
        
            mutex.release()
            empty.release()

            time.sleep(1) # remove or decrease, not sure if needed
        
            itemsInQueue = len(queue)
