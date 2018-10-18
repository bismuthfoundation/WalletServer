"""
Crude websocket client for tests
"""


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect


__version__ = '0.0.2'


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

async def statusjson(ws):
    message = '["statusjson"]'
    await command(ws, message)


async def test():
    ws = await websocket_connect(URL)
    await getbalance(ws, "0634b5046b1e2b6a69006280fbe91951d5bb5604c6f469baa2bcd840")
    await statusjson(ws)


if __name__ == "__main__":
    ioloop = IOLoop.current()
    ioloop.run_sync(test)

