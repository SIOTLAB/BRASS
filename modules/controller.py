#!/usr/bin/env python3

# the controller:
# - discovers the topology of the network
# - establishes TCP connections with any end devices that want to make a reservation request
# - manages a queue that contains requests sent from end devices via their TCP connection
# - requests are sent into the queue, then processed via a producer-consumer setup
# - this processing involves establishing the request, then sending out a confirmation to the end device involved
# - "show my reservations" command to see reservation requests per end device

from importsAndGlobal import queue, establishedRequests, datetime, threading, ReservationRequest
from random import randint
import queueManager

def createMockReqs():
    # Temporary for testing
    #   To be removed
    global queue
    for _ in range(5):
        tmpIp1 = ".".join(str(randint(0, 255)) for _ in range(4))
        tmpIp2 = ".".join(str(randint(0, 255)) for _ in range(4))
        tmpReq = ReservationRequest(tmpIp1, tmpIp2, randint(1, 5), randint(100, 1000), "234.234.23.4.2", 3454)
        queue.put(tmpReq)

def discoverTopology(): # rerun this as needed
    return

def cleanReservations():
    for entry in establishedRequests.values():
        currentTime = datetime.datetime.utcnow()
        if entry.expirationTime < currentTime:
            establishedRequests.popitem(entry)

createMockReqs()

# CREATE THREADS
switchHandler = queueManager.SwitchHandler()
hostManager = queueManager.HostManager()

lock = threading.Lock()
reservationHandler = threading.Thread(target=queueManager.consumer, args=(queue, lock), daemon=True)

# START THREADS
switchHandler.start()
hostManager.start()
reservationHandler.start()

# WAIT FOR THREADS TO COMPLETE
switchHandler.join()
hostManager.join()
reservationHandler.join()
# hostManager.kill()

cleanReservations() # this needs to be run consistently
