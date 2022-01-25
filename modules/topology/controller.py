# Python script that the controller will run to send
# commands in order to recieve topology information from client switches

import jsonrpclib
import ssl
from pprint import pprint as print

switch = input("Switch ip: ")
username = input("Username: ")
password = input("Password: ")

url = 'https://{}:{}@{}/command-api'.format(username, password, switch)

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

print(response)