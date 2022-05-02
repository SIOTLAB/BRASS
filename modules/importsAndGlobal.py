import threading
import datetime
import queue
import networkx as nx
import json

CONTROLLER_IP = None
CONTROLLER_PORT = None
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

msgPrefix = "pfg_ip_broadcast_cl"
svrPrefix = "pfg_ip_response_serv"

queue = queue.Queue()  # global array of requests as they come in from end devices
id = 0
# naive solution that simply increments id; we can change this so that IDs are reused
establishedRequests = {}
ips = {}
usernames = {}
passwords = {}
topology = nx.Graph()
resMesg = json.loads(
    '{"jsonrpc": "2.0", "method": "runCmds", "params": {"version": 1,"cmds": [],"format": "json","timestamps": false,"autoComplete": true,"expandAliases": true,"stopOnError": true,"streaming": false,"includeErrorDetail": false},"id": "EapiExplorer-1"}'
)


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
