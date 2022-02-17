#!/usr/bin/python

from importsAndGlobal import CAPACITY, buffer, in_index, out_index, queue, mutex, empty, full, establishReservation, threading
import time

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