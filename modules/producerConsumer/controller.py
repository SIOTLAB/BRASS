#!/usr/bin/python

# this is just framework for now, but ultimately can be the file that facilitates a variety of other tasks/connections

# the controller:
# - discovers the topology of the network
# - establishes TCP connections with any end devices that want to make a reservation request
# - manages a queue that contains requests sent from end devices via their TCP connection
# - requests are sent into the queue, then processed via a producer-consumer setup
# - this processing involves establishing the request, then sending out a confirmation to the end device involved
# - "show my reservations" command to see reservation requests per end device

from random import randint
from pprint import pprint

class ReservationRequest:
  def __init__(self, senderIp, destIp, bandwidth, duration):
    self.senderIp = senderIp
    self.destIp = destIp
    self.bandwidth = bandwidth
    self.duration = duration
    self.id = None # figure out what this should be initialized to

queue = [] # global array of requests as they come in from end devices

for i in range(10):
    tmpIp1 = ".".join(str(randint(0, 255)) for _ in range(4))
    tmpIp2 = ".".join(str(randint(0, 255)) for _ in range(4))
    tmpReq = ReservationRequest(tmpIp1, tmpIp2, randint(1, 5), randint(10, 100))
    queue.append(tmpReq)

id = 0 # naive solution that simply increments id; we can cahnge this so that IDs are reused
establishedRequests = {}

def discoverTopology():
    return 0

def establishTcp():
    return 0

def establishReservation(resReq):
    # generate an ID for this reservation
    # return the ID generated and send to the end device
    id = 0
    currentId = id
    id += 1
    resReq.id = currentId

    pprint(vars(resReq))
    # do whatever it takes to establish the reservation with other devices

    establishedRequests[currentId] = resReq
    return currentId