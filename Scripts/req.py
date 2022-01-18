#!/usr/bin/python3
import argparse
import getpass
import urllib3
import requests
import json

###
def writeToFile(filename, content):

    fd = open(filename, 'w')
    fd.write(content)
    fd.close()

###
def switchCmd(switch, username, password, outFile, inFile=None):

    url = 'https://{}:{}@{}/command-api'.format(username, password, switch)

    if inFile == None:
        payload = {'jsonrpc' : '2.0', 'method': 'runCmds', 'params': { 'version' : 1, 'cmds' : [], 'format' : 'json', 'timestamps' : False, 'autoComplete' : True, 'expandAliases' : True, 'stopOnError' : True, 'streaming' : False, 'includeErrorDetail' : False }, 'id' : 'EapiExplorer-1' }
        print('Input commands on separate lines. Input SEND to deliver the POST payload.')
        while True:
            command = input()
            if command in ['SEND', 'SND', 'S']:
                break
            payload['params']['cmds'].append(command)

    else:
        fd = open(inFile, 'r')
        payload = json.loads(fd.read())
        fd.close()

    urllib3.disable_warnings()
    r = requests.post(url, json=payload, verify=False)
    content = json.dumps(json.loads(r.text), indent=2)
    writeToFile(outFile, content)
    print(content)
###
def main(args):

    password = getpass.getpass("Password: ")
    switchCmd(args.switch, args.username, password, inFile=args.file, outFile=args.dest)

###
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Send an eAPI POST message.')
    parser.add_argument('switch', help='name or IP address of eAPI enabled switch')
    parser.add_argument('username', help='switch login information')
    parser.add_argument('-f', '--file', help='filename of input command file')
    parser.add_argument('-d', '--dest', help='filename of output file', default='output.json')
    args = parser.parse_args()

    main(args)

