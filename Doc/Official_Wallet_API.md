# Official Wallet API

The Bismuth network serves an official API to be used by light wallets.

THIS IS A WIP
---------------------------


## Endpoint

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

- label is a unique handle for convenience, can also be the hostname but won't be used to connect to
- ip is either the hostname of the server, or an IP if the server has no hostname
- active is a boolean, set to True only if the server was reachable at last check (every 5 min)  
  (and optionnaly if its blockheight is not too far from the highest one)
- clients is the total number of connected clients the server reported
- total_slots is the maximum clients the server accepts
- last active is the timestamp of the last check where the server was active.  
  For an active wallet, that is irrelevant, and would be less than 5 minutes in the past.  
  For a non active wallet, that would be 0 if it never was seen as active, or the timestamp of its last ok check.
- country - optional - is there for future use in a possible user selectable list.

New, also:

- version (wallet server version)
- height (latest block from server)

### Get a list of websocket wallet servers to connect to

> This endpoint is not available atm, contact the team if you have a need for it.

`https://api.bismuth.live/servers/wallet/websocket.json`

Returns a list of officially supported websocket wallet servers.

Each item is a dict with the following keys:  
`[label, ip, port, active, clients, total_slots, last_active, country]`

Apart from the default port changing, the structure is the very same as the native servers one.

