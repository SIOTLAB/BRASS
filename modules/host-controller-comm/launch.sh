if [ "$1" = "client" ]; then
	python discover_host.py
elif [ "$1" = "server" ]; then
	python discover_controller.py & echo $! > discover_controller.pid
else
	echo "$0" "<client/server>"
fi
