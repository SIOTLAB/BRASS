#!/usr/bin/python

import threading
import time

# Shared Memory variables
CAPACITY = 10 # this is the number of threads running at once, should be adjusted to max # of devices that can be requesting bandwidth at a time (?)
buffer = [-1 for i in range(CAPACITY)]
in_index = 0
out_index = 0

# Declaring Semaphores
mutex = threading.Semaphore()
empty = threading.Semaphore(CAPACITY)
full = threading.Semaphore(0)

queue = [7, 2, 3, 5, 6, 2, 8] # global array of requests as they come in from end devices

# Producer Thread Class
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
            print("request produced : ", nextItem)
            
            mutex.release()
            full.release()
            
            time.sleep(1)
            
            itemsInQueue = len(queue) # double check whether this is needed since queue is a global variable (is it getting updated, or is it passed by value?)
 
# Consumer Thread Class
class Consumer(threading.Thread):
    def run(self):
     
        global CAPACITY, buffer, in_index, out_index, queue
        global mutex, empty, full
     
        itemsInQueue = len(queue)
        while itemsInQueue > 0:
            full.acquire()
            mutex.acquire()
        
            item = buffer[out_index] # instead of just grabbing the item and printing it, run a function to actually make the reservation request where needed
            out_index = (out_index + 1) % CAPACITY
            print("request accepted : ", item)
        
            mutex.release()
            empty.release()
        
            time.sleep(0.5) # remove or decrease
        
            itemsInQueue = len(queue)
 
# Creating Threads
producer = Producer()
consumer = Consumer()
 
# Starting Threads
consumer.start()
producer.start()
 
# Waiting for threads to complete
producer.join()
consumer.join()