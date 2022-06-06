## src
This folder contains the source code for BRASS. The code is split up into three main sections, with those sections being the controller, scripts for switch discovery, and scripts for sending reservation requests from end hosts.

* controller -- contains all source code for running network controller
* reservatoinRequest-scripts -- contains code for sending reservation requests to controller from an end host
* switchDiscovery-scripts -- contains scripts that can be run on switches to send discovery messages to controller.

Outdated/deprecated modules
* topology -- original tests for discovering end hosts. This functionality has been merged into the main controller process.
