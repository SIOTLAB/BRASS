### reservationRequest-scripts
This folder contains the scripts for sending reservation requests to the controller from an end host in the network. It is not necessary to use these scripts (the controller will accept any JSON formatted request at the port it listens on). However these scripts give an example of what that request should look like and how to send itusing the SIOTLAB topology.

* discover_host.py is a script meant to be run on an end host for creating a reservation request.

Sample usage:
```
./discover_host.py 10.16.224.150 5002 24.224.1.2 10000 22.224.1.2 1000 20000 300 tcp
```
This will send the reservation request to a server listening at IP address 10.16.224.150 on port 5002 for incoming requests.

It will request a reservation from 24.224.1.2 on port 10000 to 22.224.1.2 on port 10000. It requests 20000 kbps of bandwidth to be reserved for 300 seconds using the tcp protocol.

> Computer Science and Engieering<br />Santa Clara University (SCU), Class of 2022
