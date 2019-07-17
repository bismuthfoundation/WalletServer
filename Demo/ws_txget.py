"""
Crude websocket client for tests
"""


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import time
from tornado.ioloop import IOLoop
from tornado.websocket import websocket_connect
from tornado.options import define, options


__version__ = "0.0.2"


URL = "ws://localhost:8155/web-socket/"

DEFAULT_PORT = 8155


async def command(ws, command):
    print('=>', command)
    ws.write_message(command)
    msg = await ws.read_message()
    if msg:
        print('<=', msg)
    else:
        print("Connection closed")


async def txget(ws, txid, addresses=None):
    if addresses is not None:
        message = '["txget", "{}", {}]'.format(txid, json.dumps(addresses))
    else:
        message = '["txget", "{}"]'.format(txid)
    await command(ws, message)


async def txgetjson(ws, txid, addresses=None):
    if addresses is not None:
        message = '["txgetjson", "{}", {}]'.format(txid, json.dumps(addresses))
    else:
        message = '["txgetjson", "{}"]'.format(txid)
    await command(ws, message)


async def get_the_txid():
    ws = await websocket_connect(URL)
    # txget is way faster if you can provide an optional recipient address or list of addresses
    if options.address == "":
        await txgetjson(ws, options.txid)
    else:
        await txgetjson(
            ws, options.txid, [options.address]
        )


if __name__ == "__main__":
    define("ip", default="127.0.0.1", help="Server IP[:port] to connect to, default 127.0.0.1")
    define("txid", help="txid to lookup")
    define(
        "address", default="", help="Address the txid relates to. Speeds up the lookup"
    )
    define("verbose", default=False, help="verbose")
    options.parse_command_line()

    if options.txid is None:
        print("--txid is mandatory")
        sys.exit()
    if options.ip != "127.0.0.1":
        if ":" in options.ip:
            URL = "ws://{}/web-socket/".format(options.ip)
        else:
            URL = "ws://{}:{}/web-socket/".format(options.ip, DEFAULT_PORT)
    print("Using {}".format(URL))

    ioloop = IOLoop.current()

    start = time.time()
    ioloop.run_sync(get_the_txid)
    print(f"took {time.time() - start:.3} seconds")
