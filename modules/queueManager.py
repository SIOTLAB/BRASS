#!/usr/bin/python

from importsAndGlobal import CAPACITY, buffer, in_index, out_index, queue, mutex, empty, full, establishReservation, threading, TCP_IP, TCP_PORT, BUFFER_SIZE
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

class Producer(threading.Thread):   #?
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
