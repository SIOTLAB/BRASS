#!/usr/bin/python

from importsAndGlobal import CAPACITY, buffer, in_index, out_index, queue, mutex, empty, full, establishReservation, threading
import socket
import time

class Discoverer(threading.Thread):
    def run(self):
        TCP_IP = '10.16.252.11'
        TCP_PORT = 5005
        BUFFER_SIZE = 20  # Normally 1024, but we want fast response

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)

        conn, addr = s.accept()
        print('Connection address:', addr)
        while 1:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            print("received data:", data)
            conn.send(data)  # echo
        conn.close()

class Producer(threading.Thread):
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

class Consumer(threading.Thread):
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