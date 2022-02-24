#!/usr/bin/python

from importsAndGlobal import CAPACITY, buffer, in_index, out_index, queue, mutex, empty, full, establishReservation, threading, TCP_IP, TCP_PORT, BUFFER_SIZE
import json
import socket
import time

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

class HostManager(threading.Thread):
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
                #   YES: the reservation could be instantiated
                # if : sent = s.sendto(svrPrefix.encode(), address)

                #   NO: the reservation could NOT be instantiated
                # if : sent = s.sendto('Reservation could not be fulfilled'.encode(), address)

                #   CLOSE: quit the host manager thread(s)
                # if : break

# class Producer(threading.Thread):   # For testing?
#     def run(self):
    
#         global CAPACITY, buffer, in_index, out_index, queue
#         global mutex, empty, full
    
#         itemsInQueue = len(queue)
        
#         while itemsInQueue > 0:
#             empty.acquire()
#             mutex.acquire()
#             nextItem = queue.pop()
#             buffer[in_index] = nextItem
#             in_index = (in_index + 1) % CAPACITY
            
#             mutex.release()
#             full.release()
            
#             time.sleep(1)
            
#             itemsInQueue = len(queue)

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
