"""
Crude websocket client for tests
"""


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect


URL = "ws://localhost:8155/web-socket/"


async def getbalance(address):
    ws = await websocket_connect(URL)
    ws.write_message('["getbalance", "{}"]'.format(address))
    msg =  await ws.read_message()
    if msg:
        print(msg)
    else:
        print("Connection closed")


if __name__ == "__main__":
    ioloop = IOLoop.current()
    ioloop.run_sync(lambda: getbalance("abcdef"))

