# WalletServer
An experimental Tornado based Wallet server for Bismuth

## Why?
A high perf wallet server, independant from a regular bismuth node.

## The tech
* One process, a single thread, a single DB connection.
* Fully Async
* Tornado based

## Candies
* Separate rotating logs, app_log and access_log
* Nice colored log console output
* Updateable with no node downtime

## Current drawbacks
* not much doc (wip)
* does not support tokens opearations yet (wip also)

# Usage

## Installation
* requires pythno 3.5+ (async/await)
* Copy the files over your regular node directory (needs some libs and config files)
* install dependencies: `pip3 install -r wallet-server-requirements.txt`
* The Bismuth node has to be running
* run `python3 wallet_server.py`

## Command line config
* --verbose : be more verbose
* --port : use an alternate port (default is 8150)

## Connect to the wallet server
The current wallet has a hardcoded port from config.  
atm, to connect to this server you have to manually edit your wallet.py file, and change the port:  
Line 65, replace  
`port = config.port`  
by  
`port = 8150  # Wallet server`

# Licence
Copyright Bismuth Foundation & Eggpool, GPL v2 licence.
