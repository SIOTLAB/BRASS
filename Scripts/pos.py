#!/usr/bin/python3
import json
import subprocess
from collections import OrderedDict


### EOS eAPI JSON TEMPLATE
cmd = {'jsonrpc' : '2.0',
    'method': 'runCmds',
    'params': { 'version' : 1,
        'cmds' : ['show int stat', 'show ip int br', 'enable', 'bash timeout 3 docker stats --no-stream'],
        'format' : 'json',
        'timestamps' : False,
        'autoComplete' : True,
        'expandAliases' : True,
        'stopOnError' : True,
        'streaming' : False,
        'includeErrorDetail' : False
        },
    'id' : 'EapiExplorer-1'
    }

with open('cmd.json', 'w') as outfile:
    json.dump(cmd, outfile)


### RUN EOS eAPI COMMAND
process = subprocess.run(['curl', '-d', '@cmd.json', '-X', 'POST', '-k', 'https://admin:$iot224-21@10.16.224.21:443/command-api'], 
# process = subprocess.run(['curl', '-d', '@cmd.json', '-X', 'POST', '-k', 'https://admin:@roi451:443/command-api'], 
    stdout=subprocess.PIPE, 
    universal_newlines=True)
out = json.loads(process.stdout)


### PRINT FULL JSON OUTPUT
print(json.dumps(out, indent=2))
quit()
 

### ORDRED DICTIONARIES
results = OrderedDict(sorted(out['result'][0]['interfaceStatuses'].items()))
ips = OrderedDict(sorted(out['result'][1]['interfaces'].items()))


### PRINT
print('interface', '\t', 'status', '\t\t', 'ip address', '\n---------', '\t', '------', '\t\t', '----------', sep = '')
for key in results:
    if key in ips:
        print(key, '\t', results[key]['linkStatus'], '\t', ips[key]['interfaceAddress']['ipAddr']['address'], '/', ips[key]['interfaceAddress']['ipAddr']['maskLen'], sep='')

    elif out['result'][0]['interfaceStatuses'][key]['linkStatus'] == 'connected':
        print(key, '\t', results[key]['linkStatus'], sep = '')

stats = out['result'][2]['messages']
for stat in stats:
    print(stat)

