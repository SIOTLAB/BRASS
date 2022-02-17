from pprint import pprint
import datetime
import threading

queue = [] # global array of requests as they come in from end devices
id = 0 # naive solution that simply increments id; we can change this so that IDs are reused
establishedRequests = {}

# shared memory variables
CAPACITY = 10 # this is the number of threads running at once, should be adjusted to max # of devices that can be requesting bandwidth at a time (?)
buffer = [-1 for i in range(CAPACITY)]
in_index = 0
out_index = 0

# declaring semaphores
mutex = threading.Semaphore()
empty = threading.Semaphore(CAPACITY)
full = threading.Semaphore(0)

def establishReservation(resReq):
    # generate an ID for this reservation
    # return the ID generated and send to the end device
    global id
    currentId = id
    id += 1
    resReq.id = currentId
    expirationTime = datetime.datetime.utcnow() + datetime.timedelta(minutes=resReq.duration)
    resReq.expirationTime = expirationTime
    pprint(vars(resReq))
    # do whatever it takes to establish the reservation with other devices

    establishedRequests[currentId] = resReq
    return currentId