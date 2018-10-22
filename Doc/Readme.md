# Reference Doc for the Bismuth Wallet servers

What is that?

WIP

## Two kind of servers, same backend

- wallet_server
- wallet_websocket


## Available commands

### addfromalias (alias)

Takes an alias (string)

Returns matching address

### addlist (address)

Returns a list with all transactions from `address`, last one first.  
Use with care.

Each transaction is  
`["block_height", "timestamp", "address", "recipient", "amount", "signature", "public_key", "block_hash", "fee", "reward", "operation", "openfield"]`

### addlistlim (address, limit=10, offset=0)

Returns a list of the latest `limit` transactions from `address` , starting at optional offset `offset`,  
most recent one first.

Each transaction is  
`["block_height", "timestamp", "address", "recipient", "amount", "signature", "public_key", "block_hash", "fee", "reward", "operation", "openfield"]`

Ex:
```
[865152, 1539630345.77, "da8a39cc9d880cd55c324afc2f9596c64fac05b8d41b3c9b6c481b4e", 
"d2f59465568c120a9203f9bd6ba2169b21478f4e7cb713f61eaa1ea0", 0, "YUVtPJfHGQYTIEjo3V2aXPwraHmYUOppYNEHlfD3dJ/NH8vhMdNrIuA/KGR0Cka0pV/5KwmbUqyYX5ezFW7kMk4zAjOu6kDC4Glh9PBMRW0HYYrnnD8e+VyXH3QeU8wC+mMZFGTvZnwmp+NCUgCZegjLlCfxJ14HrK5ZNJ83xNC7dMH2CX8SbP7mZGaaBOWnVzNYjj1SvD3JcgK+WsGYMaa6MkMRFkjMCUY0S11O7B9qfxAWSNmjfPFlsq3iQMxRBZD7Uw30NRquZ2rVnbo0bsTauC0rDnn4wiM6EMZqYpKrWf907BSzfTe2N2Oi2nV3X4Yw6Rft7fxG5PsoHAyAfKAWTFVaCqXtNKSylGgVEWaxMIsXa5/bIHWELfuVwbwFQsp7ESN/5XxybqXh8XGIAzeJOwDfv+qquCdBTfQXtwOc8hXhoCpDMI4DjSJqo/q/6Ve1TvvP8Eg1VzkiIWrJAbP5PljyhEd/GMes1kN7hl20cty4vPeBlRFP85vz4SwfvRAKAUlwz9K+JkHZaBibYfazcEHcewa7PSMtMmsdtkMl0bdz56HOpyMJYXK6T3rYZVO7wlXScCV6rebmEKsg0yfjDSRPKYaztGL/8iNonNis04bdIOL4UzYgUYHfJt/wzUzH5tZ2ykIvuwVCfbhT2S2QDKcmDeFvPhaHS4IZJdg=", 
"LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQ0lqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FnOEFNSUlDQ2dLQ0FnRUFwbjBoM3BiZkZMcUJzdy92ZGw3ZAp5Z0xrNWFpUW1tZlhaNzRQTE56eVQwb3FTNWJORUZhSXIzdVNwUjk4WG84Rm5lOGhjbkxvVFB0Y1lhWndUWDJECjRjakxhYm9HaWxkY1l4Vkt3ajNRQlh....0WFdXLzliYUw3bGUvVXhwbTFXaEpQRDUKM1RmemJBSy8wNE9MT3dxc2RjdFBTbUp1cHRiYVVwTTNIeEtGbFBQemFIZ2NQRW55VC9HRHJwUUJxdXFJKzVkTApabzBXZ2ZXMEtzRTFiVXdWNTJUOEhnblBDck9EbnczeUhFVVdyTjNMZUszZjFkNnQvM200Ujc4TmJUQzJlT0lsCnpvNjlvRTFyMzJnWUp6dndwcXJwNGYwQ0F3RUFBUT09Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQ==", 
"325e8f26b6ed9b8d0601c02fcefbf2871e4211e15f7a0459eb208698", 0.01006, 0, "token:transfer", "egg:50"]
```

### addlistlimjson (address, limit=10, offset=0)

json version of `addlistlim`.  
Returns a list of the latest `limit` transactions from `address` , last one first.  
Each transaction is a dict, with the keys being  
`["block_height", "timestamp", "address", "recipient", "amount", "signature", "public_key", "block_hash", "fee", "reward", "operation", "openfield"]`


### aliascheck (alias)

Takes an alias (string)

Sends back "Alias free" or "Alias registered"

## aliasesget (addresses)

Takes a list of addresses to resolve.  

Returns the list of aliases. 

### aliasget (address)

Takes an address.

Sends back the matching alias if any.

### annget

Get the current on chain announce message.

### annverget

Returns the current node version currently announced on the chain.

### balanceget (address)

Returns current balance for given `address`.

Returns  
`[balance, total_credits, total_debits, total_fees, total_rewards, balance_no_mempool]`

Ex:
`["98.34764109", "27908.23206709", "27852.10000000", "0.98335000", "43.19892400", "98.34764109000224"]`


### balancegetjson (address)

Verbose version of `balanceget`, as a keyed json object rather than a bare list.

### blocklast

Returns the latest coinbase transaction from the local node.  
The latest block height is part of the `statusjson` output and does not need that command.  
This call should not be part of regular wallet operation.

Returns
`["block_height", "timestamp", "address", "recipient", "amount", "signature", "public_key", "block_hash", "fee", "reward", "operation": "nonce"}`

Ex:
`[872105, 1540050862.85, "3d2e8fa99657ab59242f95ca09e0698a670e65c3ded951643c239bc7", "3d2e8fa99657ab59242f95ca09e0698a670e65c3ded951643c239bc7", 0, "Vs8WyVwmSV9J3OdliuHTOcLy6ZF1x+wjg7qGTMiv5oWfe7t6vK5wBEvqD/j4BOvjKrgWoXs84rCzM1JLGPuUCgbCgfINrFCdo+y1lKIbioUiI2PjCWatJuZCBGMkWKzvN0cTFi5yh0jnmkq2BG2m7uNWnrJUsGfzA951WnlUxylQAEX5pVZRvWaGR6P3+4iz+yZ.....1TlpOT0xhN1VmRjhOK3pFSEVWCjZDU3lveWpTZkdNTjBMVk1MK29xL0trQ0F3RUFBUT09Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQ==", "325586170c2a53231c2d44b349159e9bccd00616c963e6f08ea19cb8", 0, 12.45579, "0", "00000000000000000000000000000000000000000000000000003299>51051:;9200"]`

### diffget

Get current net diff from the companion node.  
Same as statusget[8].  
cached.  

Ex:  
`111.8`

### mpget

Returns the list of transactions currently in mempool.  

Each transaction is  
`["block_height", "timestamp", "address", "recipient", "amount", "signature", "public_key", "block_hash", "fee", "reward", "operation", "openfield"]`

### mpgetjson (address)

Verbose version of `mpget`, with each transaction being a keyed json object rather than a bare list.


### mpinsert (signed_transaction):

Takes a full signed transaction in the correct format (very sensitive)  
and send it for insertion into the local node mempool.

Sends back the mempool insert message (string)

### statusget
*Deprecated*  
The newest wallet clients should rather use "statusjson" that returns more info, than this call.

Get status info from the companion node.  
Cached for a small time.  



Returns 
`[node_address, nodes_count, nodes_list, threads_count, uptime, peers.consensus, peers.consensus_percentage, VERSION, diff, server_timestamp]`

Ex:  
`["f67350e6e66fba4bc6f364a50f403a33c8b84b670d1fc762318aaa32", 17, ["51.15.46.90", "51.15.254.16", "51.15.211.156", "91.121.87.99", "176.31.245.46", "51.15.118.29", "198.245.62.30", "188.165.199.153", "46.105.43.213", "51.15.201.253", "51.15.213.94", "66.70.181.150", "91.121.77.179", "163.172.222.163", "51.15.47.212", "31.31.75.71", "127.0.0.1"], 22, 46151, 868704, 100.0, "4.2.8", [110.9695450958, 110.9695450958, 1.3199999332427979, 110.9689280571, 61.51417361117072, 37246896409942.2, 0.0006170386529355149, 868704], "1539846617.79"]`

node_address is potentially anonymized.  

peers.consensus is the list of the peers IP in consensus.  

diff is a list with several info related to the diff adjustment algorithm:  
`[difficulty, difficulty_dropped, time_to_generate, diff_previous_block, block_time, neetwork_hashrate, diff_adjustment, block_height]`  

- difficulty_dropped is a lower difficulty that can be used if the current block is hard to find. Part of tail removal.  
  You can ignore that one, just use difficulty.
- time_to_generate is the last block time  
- block_time is the average block time over the last 1440 blocks (=24H roughly, used by the difficulty feedback controler)


### statusjson
*superceed the deprecated "statusget" command*

Get extended status info from the companion node.  
Cached for a small time.  

Returns a json dict 
```
{"protocolversion": "mainnet0018", 
  "address": "3a33c8b84b670d1fc762318aaa32f67350e6e66fba4bc6f364a50f40", 
  "walletversion": "4.2.8", "testnet": false, "blocks": 868694, 
  "timeoffset": 0, "connections": 16, 
  "connections_list": ["198.245.62.30", "176.31.245.46", "51.15.118.29", "46.105.43.213", "51.15.213.94", "91.121.77.179", "91.121.87.99", "188.165.199.153", "127.0.0.1", "163.172.222.163", "66.70.181.150", "51.15.254.16", "51.15.201.253", "51.15.46.90", "51.15.211.156", "51.15.47.212"], 
  "difficulty": 110.9689516728, "threads": 21, "uptime": 45761, 
  "consensus": 868694, "consensus_percent": 93.75, "server_timestamp": "1539846227.82"}
```


### tokensget (address):

Takes an address.

Returns the list of tokens and amount for that address.


### txget (txid, addresses=[]):
*Wallet server only command, this is __not__ a regular node command* 

Takes a txid (56 char, base64).  
Takes an optional list of possible recipient addresses (the known wallet addresses)

> Txget is way faster if you can provide an optional recipient address or list of possible recipient addresses

Returns the full transaction of an error message   
`["Ko", "No such TxId"]`

Each transaction is  
`["block_height", "timestamp", "address", "recipient", "amount", "signature", "public_key", "block_hash", "fee", "reward", "operation", "openfield"]`

Ex:
```
[873833, 1540156329.18, "0634b5046b1e2b6a69006280fbe91951d5bb5604c6f469baa2bcd840", 
"d2f59465568c120a9203f9bd6ba2169b21478f4e7cb713f61eaa1ea0", 0, 
"Zr7jd0cYxshZiTdZVlSH3vrS9e7Ixb+VZ+KDCcKc3+noS+2lVy7qE/qa1KECugNSIhOUcMj0S3mx2gG7y8tIjLnnw/qzZViXaMMOUOsyX7HRfuP4ujh3xJyeTTpAiXt6SaOPIz91HdU6hvuegffKYvmfcQGHgtpEOOoSSC39DWjzrcNMzmjV1SxlpcWUeQyoJH9DR83eq6553NnZMrRehiD0TBsx3QclE9s4q862s7gCZ88RMLWtCDxCsH4QOiAUbGo3DAZLTXDN7VU3twseYgq3wy7qAwrOOTcZI7Tl02QNb2GLfy0Lwep//BsZ3h8ZaUiSkcFwyzxr7lhlvcXg/M6Mmkz9F2CMcpvKUhZ2GtaM1UtGbW6KrXQvdcKqT6rupl9V8zX9zeRtGNdLnE3Ihlv6z8+MiUKSvVm7jSh9Npuau3eNqivktypG3emNAUxffhOx3FKZpZNpzuUtcQC8HHvW8E10Ig5tYp6LciKxTzoqIV/JiQ12gETQrh0PrH4wTI2ZNs83kNXKDHSV0DFFAYAW20/iLehsUka7fj5xQthjr6ECTkQpxmKJ9WPA587oltOvLYKnN4k+BJWSGvavkXYk+SsbS4/eQQ1jLWOISw+8SH4vkbcH4Hop31b44rinCIGc4mGjeIwWEvgnEOPXiFulmyIDwZ+YO5gVrDuhhFo=", 
"LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQ0lqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FnOEFNSUlDQ2dLQ0FnRUFvQm9wTnpXTURuclNzMnU4aldJUgp2SG4zMWE3U0ZPczdBOFdUQUF0cEk0L2NTbjlXOVZnVmMrdXJOS2U0eTB1NVJLVWRRTGI0WUpwb3F3ai94b0NYCkg0Zk9YR3BtUGJFd3hyTjljeFpEdDFyazJ4OHV0RkFhOU92ZlFIS1NXV2dWTlAxZDZ1L3k0REhiYzVSTllwUi8Kb1ByOHVscWtxeEJIUGJXOEkya2duWGlkSDM3ZlpOYmhFaXMxeW43M0d4Q2VwL3Z1TWVwOVZKc2gwWUE0dFRTWgpCZUw5OUhTNEhBRCtOM2s2MVlNOWxsSm1QVlVEekpPMEN2d29ZNHdDUjhIdW1LenJTcnhtYUxEN1NTa3hMVlp0ClBNWGNnQjBQK0V4UTk3emxBVHovZkFrWkFXVGYyY01MWG1DeDRWMUxBNGQvOEtXS3VXdXd1dDYwM3grNHBVYUYKbE9kdTlnVmpma2xTNWRPNFByZDNxbEhiMC9NakI2eUFabUpzbnBIaU5TZW1nd0hRYi8rZk04MEdSOGZYWTFOSgpuMTd2a2Q4KzdVV1ZxeHBVVk5CcTU1RmQ3NExZNVAySFJoM0tyNXlrMkxZM1dqbmV4ZXpSWW95ME11SE9lNVd4CkJFYnlob3JzSGhydTB6elRNbHRkL2g0eWgvUU9HWkxTaUc1OFJ3UFZZRW9RQk1jdThXKzJQdjBRbkhCejRyRzQKdFBHV280WWJkTzREb2VNLytORkI2Y0x1Ky9IQ1J4eHp2Y2tZOS85NXZHZU1LU1hWZEdNWm5BSGVGT1BibnJseQpFRVR5STVLUk5QWjVOUEZMTVpETGN6K1lVRjVrMGd1M1ZUUStIV1gyZ1RiVTdFSENYcWpKRVpONFYyS1hsMzhRCjJZRk42ZGd6WU0rTnlVTENrZTVWV05NQ0F3RUFBUT09Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQ==", 
"13a022d61eec403b8966ebe4036522399f76a5ca8fa34609be7748e9", 
0.01021, 0, "", "msg=This is a message"]
```

### txgetjson (txid, addresses=[]):
*Wallet server only command, this is __not__ a regular node command* 

Like txget, but sends back a dict, with the keys being  
`["block_height", "timestamp", "address", "recipient", "amount", "signature", "public_key", "block_hash", "fee", "reward", "operation", "openfield"]`

Ex:
```
{"block_height": 873833, "timestamp": 1540156329.18, 
"address": "0634b5046b1e2b6a69006280fbe91951d5bb5604c6f469baa2bcd840", 
"recipient": "d2f59465568c120a9203f9bd6ba2169b21478f4e7cb713f61eaa1ea0", 
"amount": 0, 
"signature": "Zr7jd0cYxshZiTdZVlSH3vrS9e7Ixb+VZ+KDCcKc3+noS+2lVy7qE/qa1KECugNSIhOUcMj0S3mx2gG7y8tIjLnnw/qzZViXaMMOUOsyX7HRfuP4ujh3xJyeTTpAiXt6SaOPIz91HdU6hvuegffKYvmfcQGHgtpEOOoSSC39DWjzrcNMzmjV1SxlpcWUeQyoJH9DR83eq6553NnZMrRehiD0TBsx3QclE9s4q862s7gCZ88RMLWtCDxCsH4QOiAUbGo3DAZLTXDN7VU3twseYgq3wy7qAwrOOTcZI7Tl02QNb2GLfy0Lwep//BsZ3h8ZaUiSkcFwyzxr7lhlvcXg/M6Mmkz9F2CMcpvKUhZ2GtaM1UtGbW6KrXQvdcKqT6rupl9V8zX9zeRtGNdLnE3Ihlv6z8+MiUKSvVm7jSh9Npuau3eNqivktypG3emNAUxffhOx3FKZpZNpzuUtcQC8HHvW8E10Ig5tYp6LciKxTzoqIV/JiQ12gETQrh0PrH4wTI2ZNs83kNXKDHSV0DFFAYAW20/iLehsUka7fj5xQthjr6ECTkQpxmKJ9WPA587oltOvLYKnN4k+BJWSGvavkXYk+SsbS4/eQQ1jLWOISw+8SH4vkbcH4Hop31b44rinCIGc4mGjeIwWEvgnEOPXiFulmyIDwZ+YO5gVrDuhhFo=", 
"public_key": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQ0lqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FnOEFNSUlDQ2dLQ0FnRUFvQm9wTnpXTURuclNzMnU4aldJUgp2SG4zMWE3U0ZPczdBOFdUQUF0cEk0L2NTbjlXOVZnVmMrdXJOS2U0eTB1NVJLVWRRTGI0WUpwb3F3ai94b0NYCkg0Zk9YR3BtUGJFd3hyTjljeFpEdDFyazJ4OHV0RkFhOU92ZlFIS1NXV2dWTlAxZDZ1L3k0REhiYzVSTllwUi8Kb1ByOHVscWtxeEJIUGJXOEkya2duWGlkSDM3ZlpOYmhFaXMxeW43M0d4Q2VwL3Z1TWVwOVZKc2gwWUE0dFRTWgpCZUw5OUhTNEhBRCtOM2s2MVlNOWxsSm1QVlVEekpPMEN2d29ZNHdDUjhIdW1LenJTcnhtYUxEN1NTa3hMVlp0ClBNWGNnQjBQK0V4UTk3emxBVHovZkFrWkFXVGYyY01MWG1DeDRWMUxBNGQvOEtXS3VXdXd1dDYwM3grNHBVYUYKbE9kdTlnVmpma2xTNWRPNFByZDNxbEhiMC9NakI2eUFabUpzbnBIaU5TZW1nd0hRYi8rZk04MEdSOGZYWTFOSgpuMTd2a2Q4KzdVV1ZxeHBVVk5CcTU1RmQ3NExZNVAySFJoM0tyNXlrMkxZM1dqbmV4ZXpSWW95ME11SE9lNVd4CkJFYnlob3JzSGhydTB6elRNbHRkL2g0eWgvUU9HWkxTaUc1OFJ3UFZZRW9RQk1jdThXKzJQdjBRbkhCejRyRzQKdFBHV280WWJkTzREb2VNLytORkI2Y0x1Ky9IQ1J4eHp2Y2tZOS85NXZHZU1LU1hWZEdNWm5BSGVGT1BibnJseQpFRVR5STVLUk5QWjVOUEZMTVpETGN6K1lVRjVrMGd1M1ZUUStIV1gyZ1RiVTdFSENYcWpKRVpONFYyS1hsMzhRCjJZRk42ZGd6WU0rTnlVTENrZTVWV05NQ0F3RUFBUT09Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQ==", 
"block_hash": "13a022d61eec403b8966ebe4036522399f76a5ca8fa34609be7748e9", 
"fee": 0.01021, "reward": 0, "operation": "", "openfield": "msg=This is a message"}
```



## Other info

### Bismuth address

56 hex chars, with a-f being lowercase.

Matching regexp: `[a-f0-9]{56}`

### Bismuth transaction id

The txid of a transaction are the first 56 chars of the transaction signature.  
This signature is encoded as a base64 encoded string in the above messages.
