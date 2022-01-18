#!/usr/bin/python3
import time
import random
from enum import IntEnum

# commands = [
#         ['show interfaces status connected'],
#         ['show ip interface brief'],
#         ['show ip arp resolve'],
#         ['show qos interfaces ethernet 15'],
#         ['show qos interfaces ethernet 16'],
#         ['show qos interfaces ethernet 25'],
#         ['enable','configure','interface ethernet 15','tx-queue 3','no priority'],
#         ['enable','configure','interface ethernet 15','tx-queue 3','priority strict']
#         ]

# while True:
#     payload = random.choice(commands)
#     print(payload)
#     time.sleep(1)


###
class Choice(IntEnum):
    RANDOM = 1
    CUSTOM = 2
print(list(map(int, Choice)))

choice = int(input())
if choice in list(map(int, Choice)):
    print (Choice(choice).name)

print("Choose traffic type:\n\t", Choice.RANDOM.value, ") Random\n\t", Choice.CUSTOM.value, ") Input a command", sep='')

if choice == Choice.CUSTOM.value:

# if choice not in list(map(int, Choice)):
#     print("Invalid")
# else:
#     print("Great choice!")
