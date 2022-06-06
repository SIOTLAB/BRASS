## Controller code

This folder contains the source code for running the controller. controller.py is the main driver of the controller code. It makes use of global constants defined in importsAndGlobal.py, and the code for the individual threads and helper functions is contained in queueManager.py.

The controller can be run using the command
```
./contoller.py <controller ip> <port>
```
Controller ip is the IP address of the device that runs the controller process. 
Port will be the port assigned to the controller for switch discovery, and port+1 will be assigned to end host reservation requests

For example,
```
./controller.py 10.16.224.151 5001
```
Will start the controller and try to bind the IP address to 10.16.224.151, port 5001 for switch discovery, and the same ip at port 5002 for end host requests.

> Computer Science and Engineering<br />Santa Clara University (SCU), Class of 2022
