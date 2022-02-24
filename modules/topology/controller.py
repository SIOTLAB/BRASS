#!/usr/bin/env python3
# Python script that the controller will run to send
# commands in order to recieve topology information from client switches

from lib2to3.pytree import BasePattern
from multiprocessing.sharedctypes import Value
import jsonrpclib
import ssl
import networkx as nx
import matplotlib

RACK = 224

ips = {
    "sw21-r224" : "10.16.224.21",
    "sw22-r224" : "10.16.224.22",
    "sw23-r224" : "10.16.224.23",
    "sw24-r224" : "10.16.224.24"
}

username = "admin"
base_password = "$iot" + str(RACK) + "-"

G = nx.Graph()

for name, ip in ips.items():
    print("==== " + name + " lldp info ====")
    sw_num = name[2:4]
    password = base_password + sw_num
    url = 'https://{}:{}@{}/command-api'.format(username, password, ip)

    # SSL certificate check keeps failing; only use HTTPS verification if possible
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context


    eapi_conn = jsonrpclib.Server(url)

    payload = ["show lldp neighbors"]
    response = eapi_conn.runCmds(1, payload)[0]

    G.add_node(name)
    neighbors = response['lldpNeighbors']

    # print(neighbors)

    for n in neighbors:
        print(n['port'])

        payload[0] = "show interfaces " + n['port'] + " status"
        response = eapi_conn.runCmds(1, payload)[0]

        neighbor_name = n["neighborDevice"]
        neighbor_ip = ips[neighbor_name]

        G.add_edge(name, neighbor_name)
        bandwidth = response['interfaceStatuses'][n['port']]['bandwidth']
        G[name][neighbor_name]['bandwidth'] = bandwidth
        print(neighbor_name + " : " + neighbor_ip)

    # print("-" * 30)
    print("\n")

labels = nx.get_edge_attributes(G, "bandwidth")
pls = nx.spring_layout(G)
nx.draw_networkx(G, pls)
nx.draw_networkx_edge_labels(G, pls, labels)

matplotlib.pyplot.show()