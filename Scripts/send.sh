#!/bin/sh

cat << EOF >> cmd.json
{
  "jsonrpc": "2.0",
  "method": "runCmds",
  "params": {
    "version": 1,
    "cmds": [
      "show ip int br"
    ],
    "format": "json",
    "timestamps": false,
    "autoComplete": true,
    "expandAliases": true,
    "stopOnError": true,
    "streaming": false,
    "includeErrorDetail": false
  },
  "id": "EapiExplorer-1"
}
EOF

if [ $1 ]; then
    curl -d @cmd.json -X POST -k https://admin:@roi451:443/command-api | python -m json.tool
else
    curl -d @cmd.json -X POST -k https://admin:@roi451:443/command-api
fi
