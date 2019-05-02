# WalletServer
A Wallet server for Bismuth, powering light wallets.

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
* not much doc (wip, see https://github.com/bismuthfoundation/WalletServer/tree/master/Doc )

# Usage

See https://github.com/bismuthfoundation/WalletServer/tree/master/Demo


** IMPORTANT **
===============

CURRENTLY BEING REWRITEN  
========================

It now lives in a directory of its own and has its own config.
==============================================================


## Installation
* requires python 3.6+ (async/await)
* Copy the files over your regular node directory (needs some libs and config files from bismuth core)
* install dependencies: `pip3 install -r wallet-server-requirements.txt`
* Make sure you don't use ram mempool: in config.txt, set `mempool_ram_conf=False`
* The Bismuth node has to be running
* run `python3 wallet_server.py`

## Command line config
* --verbose : be more verbose
* --port : use an alternate port (default is 8150)

## Connect to the wallet server
The current wallet uses a hardcoded port from config.  
Atm, to connect to this server you have to manually edit your wallet.py file, and change the port:  
Line 65, replace  
`port = config.port`  
by  
`port = 8150  # Wallet server`

> A workaround would be to run your bismuth node on an alternate port, and use default 5658 port as the wallet server port.

# Changelog

## 0.1.7

New functions added to ease dApps dev work.  
See https://github.com/bismuthfoundation/WalletServer/tree/master/Doc for commands reference.

## 0.1.1

Major refactor to support the websocket server as well.

## 0.0.4

Upgrade is more than recommended

* more status info about open file descriptors
* fixed a pretty bad socket descriptors leak
* alert if ulimit is too small on launch
* prints current file limits at launch
* psutil is a new pip requirement
* previous requirements were wrong, python 3.6+ is required.

## 0.0.3
* More verbose by default
* Enforce MAX_CLIENTS (see wallet_server.py, 500 by default)
* Status display with connected clients # every 30 sec

## 0.0.2
First release version


# Licence
Copyright Bismuth Foundation & Eggpool, GPL v2 licence.
