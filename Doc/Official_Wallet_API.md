# Official Wallet API

The Bismuth network serves an official API to be used by light wallets.

## Endpoint

Base URL is   
`https://api.bismuth.live/servers/wallet/`

Data is returned as json, and is cached for 5 minutes.  
No need in querying this API more often.

## Requests

### Get a list of native wallet servers to connect to

`https://api.bismuth.live/servers/wallet/legacy.json`

Returns a list of officially supported wallet servers.

Each item is a dict with the following keys:  
`[label, ip, port, active, clients, total_slots, last_active, country]`

### Get a list of websocket wallet servers to connect to

`https://api.bismuth.live/servers/wallet/websocket.json`

Returns a list of officially supported wallet servers.

Each item is a dict with the following keys:  
`[label, ip, port, active, clients, total_slots, last_active, country]`

