"""
Crude websocket client for tests
"""


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect


__version__ = '0.0.3'


URL = "ws://localhost:8155/web-socket/"


async def command(ws, command):
    ws.write_message(command)
    msg = await ws.read_message()
    if msg:
        print(msg)
    else:
        print("Connection closed")


async def getbalance(ws, address):
    message = '["balanceget", "{}"]'.format(address)
    await command(ws, message)
    # Json version
    message = '["balancegetjson", "{}"]'.format(address)
    await command(ws, message)

async def statusjson(ws):
    message = '["statusjson"]'
    await command(ws, message)

async def statusget(ws):
    message = '["statusget"]'
    await command(ws, message)

async def blockget(ws):
    message = '["blockget", [558742]]'
    await command(ws, message)

async def addlistlimjson(ws, address, limit, offset=0):
    message = '["addlistlimjson", ["{}", {}, {}]]'.format(address, limit, offset)
    await command(ws, message)

async def txget(ws, txid, addresses=[]):
    if len(addresses):
        message = '["txget", ["{}", {}]]'.format(txid, json.dumps(addresses))
    else:
        message = '["txget", ["{}"]]'.format(txid)
    await command(ws, message)

async def txgetjson(ws, txid, addresses=[]):
    if len(addresses):
        message = '["txgetjson", ["{}", {}]]'.format(txid, json.dumps(addresses))
    else:
        message = '["txgetjson", ["{}"]]'.format(txid)
    await command(ws, message)


async def test():
    ws = await websocket_connect(URL)
    await getbalance(ws, "0634b5046b1e2b6a69006280fbe91951d5bb5604c6f469baa2bcd840")
    await statusget(ws)
    await statusjson(ws)
    await blockget(ws)
    await addlistlimjson(ws, "0634b5046b1e2b6a69006280fbe91951d5bb5604c6f469baa2bcd840", 3)
    await addlistlimjson(ws, "0634b5046b1e2b6a69006280fbe91951d5bb5604c6f469baa2bcd840", 3, 2)
    await txget(ws, "Zr7jd0cYxshZiTdZVlSH3vrS9e7Ixb+VZ+KDCcKc3+noS+2lVy7qE/qa")
    # txget is way faster if you can provide an optional recipient address or list of addresses
    await txgetjson(ws, "Zr7jd0cYxshZiTdZVlSH3vrS9e7Ixb+VZ+KDCcKc3+noS+2lVy7qE/qa", ["d2f59465568c120a9203f9bd6ba2169b21478f4e7cb713f61eaa1ea0"])


if __name__ == "__main__":
    ioloop = IOLoop.current()
    ioloop.run_sync(test)

