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

Returns all transactions from `address` , last one first.  
Use with care.

### addlistlim (address, limit)

Returns the latest `limit` transactions from `address` , last one first.

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


### statusjson
*superceed deprecated "statusget" command*

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

Sends back the list of tokens and amount for that address.


