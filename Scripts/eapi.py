#!/usr/bin/python3
import argparse
import getpass
import jsonrpclib
from pprint import pprint
import ssl

###
def switchCmd(switch, username, password, outFile, inFile=None):

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

    if inFile is None:
        payload = []
        command_count = 0
        print('Input commands on separate lines. Input SEND to deliver the POST payload. QUIT to exit.')
        while True:
            command = input()
            if command in ['SEND', 'SND', 'S']:
                break
            elif command in ['QUIT', 'Q']:
                quit()
            payload.append(command)
            command_count += 1
    else:
        fd = open(inFile, 'r')
        payload = json.loads(fd.read())
        fd.close()

    eapi_conn = jsonrpclib.Server(url)
    response = eapi_conn.runCmds(1, payload)

    for i in range(command_count):
        pprint(response[i])

###
def main(args):

    password = getpass.getpass("Password: ")

    print('Example:\n\tshow interfaces status connected\n\tshow ip interface brief')
    while True:
        switchCmd(args.switch, args.username, password, inFile=args.file, outFile=args.dest)

###
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Send an eAPI POST message.')
    parser.add_argument('switch', help='name or IP address of eAPI enabled switch')
    parser.add_argument('username', help='switch login information')
    parser.add_argument('-f', '--file', help='file containing list of input commands')
    parser.add_argument('-d', '--dest', help='filename of output file', default='output.json')
    args = parser.parse_args()

    main(args)

