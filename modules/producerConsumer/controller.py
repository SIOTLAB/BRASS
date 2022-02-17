#!/usr/bin/python

# this is just framework for now, but ultimately can be the file that facilitates a variety of other tasks/connections

# the controller:
# - discovers the topology of the network
# - establishes TCP connections with any end devices that want to make a reservation request
# - manages a queue that contains requests sent from end devices via their TCP connection
# - requests are sent into the queue, then processed via a producer-consumer setup
# - this processing involves establishing the request, then sending out a confirmation to the end device involved
# - "show my reservations" command to see reservation requests per end device

import importsAndGlobal
from random import randint
import queueManager
class ReservationRequest:
  def __init__(self, senderIp, destIp, bandwidth, duration):
    self.senderIp = senderIp
    self.destIp = destIp
    self.bandwidth = bandwidth
    self.duration = duration # duration from when the request is established on the controller, measured in minutes
    self.expirationTime = None
    self.id = None # figure out what this should be initialized to

def createMockReqs():
    for _ in range(5):
        tmpIp1 = ".".join(str(randint(0, 255)) for _ in range(4))
        tmpIp2 = ".".join(str(randint(0, 255)) for _ in range(4))
        tmpReq = ReservationRequest(tmpIp1, tmpIp2, randint(1, 5), randint(10, 100))
        importsAndGlobal.queue.append(tmpReq)

def discoverTopology(): # rerun this as needed
    return 0

def establishTcp(): # on demand from end devices
    return 0

def cleanReservations():
    for entry in importsAndGlobal.establishedRequests.values():
        currentTime = importsAndGlobal.datetime.datetime.utcnow()
        if entry.expirationTime < currentTime:
            importsAndGlobal.establishedRequests.popitem(entry)

createMockReqs()

# create threads
producer = queueManager.Producer()
consumer = queueManager.Consumer()

# start threads
consumer.start()
producer.start()

# wait for threads to complete
producer.join()
consumer.join()

print(importsAndGlobal.establishedRequests)

cleanReservations()