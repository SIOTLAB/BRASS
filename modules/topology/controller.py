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
    # "sw23-r224" : "10.16.224.23",
}

username = "admin"
base_password = "$iot" + str(RACK) + "-"

G = nx.Graph()

for name, ip in ips.items():
    print(name + " lldp info")
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
        neighbor_name = n["neighborDevice"]
        neighbor_ip = ips[neighbor_name]
        G.add_edge(name, neighbor_name, 0)
        print(neighbor_name + " : " + neighbor_ip)

    print("--------------------------------")

G.add_edge("sw21-r224", "sw22-r224")
G.edges['sw21-r224', 'sw22-r224']['weight'] = 200
labels = nx.get_edge_attributes(G, "weight")
pls = nx.spring_layout(G)
nx.draw_networkx(G, pls)
nx.draw_networkx_edge_labels(G, pls, labels)

print(G.edges['sw21-r224', 'sw22-r224'])
matplotlib.pyplot.show()