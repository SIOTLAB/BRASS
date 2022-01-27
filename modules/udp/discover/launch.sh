#!/bin/dash

if [ "$1" = "client" ]; then
	python3 discover_client.py
elif [ "$1" = "server" ]; then
	python3 discover_server.py & echo $! > discovery_server.pid
else
	echo "$0" "<client/server>"
fi
