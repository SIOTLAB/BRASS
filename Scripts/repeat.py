#!/usr/bin/python3
import argparse
import getpass
import jsonrpclib
from pprint import pprint
import random
import time
from enum import IntEnum
import ssl

commands = [
        ['show interfaces status connected'],
        ['show ip interface brief'],
        ['show ip arp resolve'],
        ['show qos interfaces ethernet 15'],
        ['show qos interfaces ethernet 16'],
        ['show qos interfaces ethernet 25'],
        ['enable','configure','interface ethernet 15','tx-queue 3','no priority'],
        ['enable','configure','interface ethernet 15','tx-queue 3','priority strict']
        ]

###
class Choice(IntEnum):
    RANDOM = 1
    CUSTOM = 2

###
def repreatCmd(switch, username, choice, interval, duration, show):

    if choice == Choice.CUSTOM.value:
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

    elif choice == Choice.RANDOM.value:
        payload = random.choice(commands)

    password = getpass.getpass("Password: ")
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
    if interval != 0:
        duration = round(duration/interval)
    for i in range(duration):
        response = eapi_conn.runCmds(1, payload)
        if show:
            pprint(response)
        time.sleep(interval)
    # print("COMMAND:", payload, "\nRESPONSE:")

    # if choice == Choice.RANDOM.value:
    #     pprint(response)
    # elif choice == Choice.CUSTOM.value:
    #     for i in range(command_count):
    #         pprint(response[i])

###
def main(args):

    print("Choose traffic type:\n\t", Choice.RANDOM.value, ") Random\n\t", Choice.CUSTOM.value, ") Input a command", sep='')
    choice = int(input())
    if choice not in list(map(int, Choice)):
        print("Invalid option")
    else:
        repreatCmd(args.switch, args.username, choice, int(args.interval), int(args.duration), args.show)

###
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Send an eAPI POST message.')
    parser.add_argument('switch', help='name or IP address of eAPI enabled switch')
    parser.add_argument('username', help='switch login information')
    parser.add_argument('-i', '--interval', help='time between repeated commands', default=1)
    parser.add_argument('-d', '--duration', help='amount of time to run', default=300)
    parser.add_argument('-o', '--show', help='print output', default=False)
    args = parser.parse_args()

    main(args)

