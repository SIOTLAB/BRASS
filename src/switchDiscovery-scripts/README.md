### switchDiscovery-scripts

This folder contains the python scripts which are used for switch discovery. These scripts can be run on Arista switches by dropping into a bash shell from the CLI. This provides access to a Linux style prompt which can run simple Python (verison 2.7) programs.

* controller.py contains initial discovery testing, but has been incorporated into the main controller process.
* switch.py contains the script that sends a discovery message to the controller. This file should be run on NETWORK SWITCHES an admin would like discovered

For example, after SSHing into a switch, your prompt should look as follows:
```
Last login: Tue May 24 16:03:23 2022 from 10.16.252.10
sw21-r224.03:55:35#
```

Then, run the following commands to send a discovery message
```
Last login: Tue May 24 16:03:23 2022 from 10.16.252.10
sw21-r224.03:56:52#bash

Arista Networks EOS shell

[admin@sw21-r224 ~]$ python switch.py
```

> Computer Science and Engineering<br />Santa Clara University (SCU), Class of 2022
