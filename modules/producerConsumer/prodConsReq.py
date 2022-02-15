#!/usr/bin/python

import threading
import time

import controller

# Shared Memory variables
CAPACITY = 10 # this is the number of threads running at once, should be adjusted to max # of devices that can be requesting bandwidth at a time (?)
buffer = [-1 for i in range(CAPACITY)]
in_index = 0
out_index = 0
queue = controller.queue # ensure that these actually point to the same obj

# Declaring Semaphores
mutex = threading.Semaphore()
empty = threading.Semaphore(CAPACITY)
full = threading.Semaphore(0)

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
        
            item = buffer[out_index]
            out_index = (out_index + 1) % CAPACITY

            controller.establishReservation(item)
            print("request accepted : ", item)
        
            mutex.release()
            empty.release()
        
            time.sleep(0.5) # remove or decrease, not sure if needed
        
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