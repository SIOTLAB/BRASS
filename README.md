# BRASS - Bandwidth Reservation on Arista Switching Systems
A Senior Design project by Tyler Tivadar, Conrad Park, and Angelus McNally.

Bandwidth Reservation on Arista Switching Systems (BRASS) is a fully programmable, controller-based, resource reservation handler for remote Quality of Service (QoS) enforcement. This handler serves as a low-cost alternative to enterprise solutions and is targeted toward resource-limited Local Area Networks (LANs) handling mission-critical applications.

The system uses a central controller to register network switches and maintain an updated network topology in order to enforce reservations in a given network when requests are made by participating end devices.

More detailed information, including system architecture and usage, can be found in the subdirectory README files:
* src -- contains all source code used for the project, including controller and host/switch side scripts
* images -- contains images relevant to project such as lab topology
* scripts -- contains scripts for automating of tests and testing of features
* testData -- contains csv files of test data and svg files of graphs/plots of data
