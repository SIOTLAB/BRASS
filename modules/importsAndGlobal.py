import threading
import datetime
from queue import Queue
import networkx as nx

TCP_IP = None
TCP_PORT = None
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

msgPrefix = "pfg_ip_broadcast_cl"
svrPrefix = "pfg_ip_response_serv"

queue = Queue()  # global array of requests as they come in from end devices
id = 0
# naive solution that simply increments id; we can change this so that IDs are reused
establishedRequests = {}
ips = {}
usernames = {}
passwords = {}
topology = nx.Graph()


class ReservationRequest:
    def __init__(self, senderIp, destIp, bandwidth, duration, port):
        self.senderIp = senderIp
        self.destIp = destIp
        self.bandwidth = bandwidth
        self.duration = (
            duration
        )  # duration is measured from when the request is established on the controller, scale is in seconds
        self.senderPort = port
        self.expirationTime = None
        self.id = None  # id is added when reservation is established
