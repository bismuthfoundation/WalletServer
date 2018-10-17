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

Get thhe current on chain announce message.

### annverget

Returns the current node version currently announced on the chain.

### balanceget (address)

Returns current balance for given `address`.

### blocklast

Returns the current block height of the local node.

### diffget

Get current net diff from the companion node.  
Same as statusget[8].  
cached.  

Ex:  
`111.8`

### mpget

Returns the list of transactinos currently in mempool.

### mpinsert (signed_transaction):

Takes a full signed transaction in the correct format (very sensitive)  
and send it for insertion into the local node mempool.

Sends back the mempool insert message (string)

### statusget

Get status info from the companion node.  
Cached for a small time.  

Returns 
`[node_address, nodes_count, nodes_list, threads_count, uptime, peers.consensus, peers.consensus_percentage, VERSION, diff, server_timestamp]`

### tokensget (address):

Takes an address.

Sends back the list of tokens and amount for that address.


