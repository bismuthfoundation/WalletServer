"""
A Tornado based wallet server for Bismuth, with websocket server.

EggdraSyl -October 2018

pip3 install -r requirements.txt
"""

# TODO: background status taks

# TODO: limit clients #

# TODO: send copies of txs directly to pool nodes? Ok if wallet servers are whitelisted.


import logging
import json
import os
import sys
import time
from logging.handlers import RotatingFileHandler

import aioprocessing
import psutil
import tornado.gen
import tornado.log
import tornado.util
from tornado.ioloop import IOLoop
from tornado.options import define, options
import tornado.web
import tornado.httpserver
import tornado.websocket
import tornado.options

# Bismuth specific modules
import modules.config as config
# from modules.helpers import *
from modules.sqlitebase import SqliteBase
from modules.node_interface import NodeInterface


__version__ = '0.0.2'


NODE_INTERFACE = None


class ChannelHandler(tornado.websocket.WebSocketHandler):
    """
    Handler for a websocket channel
    """

    @classmethod
    def urls(cls):
        return [
            (r'/web-socket/', cls, {}),  # Route/Handler/kwargs
        ]

    def initialize(self):
        pass

    def open(self):
        """
        Client opens a websocket
        """
        global access_log
        global app_log
        access_log.info("open")

    async def send_ko(self, reason):
        await self.write_message('["Ko", "{}"]'.format(reason))

    async def on_message(self, message):
        """
        Message received on channel
        """
        app_log.info("Message {}".format(message))
        message = json.loads(message)
        # TODO: check with message[0] that we have the right number of params
        params_count = NODE_INTERFACE.param_count_of(message[0], ['none'])
        if params_count < 0:
            await self.send_ko("Unknown command")
            return
        # string, or dict that will be json encoded
        res = await NODE_INTERFACE.call_user(message)
        await self.write_message(json.dumps(res))

    def on_close(self):
        """
        Channel is closed
        """
        if self.close_code:
            access_log.info("close, code {} reason {}".format(self.close_code, self.close_reason))

    def check_origin(self, origin):
        """
        Override the origin check if needed
        """
        return True


async def getrights(ip):
    try:
        result = ['none']
        if ip in CONFIG.allowed:
            result.append("admin")
        return result
    except Exception as e:
        app_log.warning("Error getrights {}".format(str(e)))


def start_server(port):
    global NODE_INTERFACE

    mempool = SqliteBase(options.verbose, db_path=CONFIG.node_path + '/', db_name='mempool.db', app_log=app_log)
    db_name = 'ledger.db'
    if CONFIG.testnet:
        db_name = 'test.db'
    ledger = SqliteBase(options.verbose, db_path=CONFIG.db_path+'/', db_name=db_name, app_log=app_log)
    NODE_INTERFACE = NodeInterface(mempool, ledger, CONFIG)

    app = tornado.web.Application(ChannelHandler.urls())

    # Setup HTTP Server
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port)
    # http_server.listen(port, LISTEN_ADDRESS)

    # Start IO/Event loop
    io_loop = tornado.ioloop.IOLoop.current()
    try:
        io_loop.start()
    except KeyboardInterrupt:
        stop_event.set()
        io_loop.stop()
        app_log.info("exited cleanly")


if __name__ == "__main__":
    global app_log
    global access_log
    global stop_event
    global start_time
    global process

    CONFIG = config.Get()
    CONFIG.read()
    #
    is_testnet = CONFIG.testnet
    PORT = CONFIG.websocket_port
    MAX_CLIENTS = CONFIG.max_clients

    define("port", default=PORT, help="port to listen on")
    define("verbose", default=False, help="verbose")
    options.parse_command_line()

    # TODO
    """
    if CONFIG.mempool_ram_conf:
        print("Incompatible setting detected.")
        print("Please edit config.txt, set mempool_ram_conf=False and restart node")
        sys.exit()
    """

    # TODO: print settings

    if not os.path.isfile(CONFIG.node_path + '/mempool.db'):
        print("mempool.db not found.")
        print("Please edit config.txt, check mempool_ram_conf=False and restart node.")
        sys.exit()

    start_time = time.time()

    stop_event = aioprocessing.AioEvent()  # Event()

    lock = aioprocessing.AioLock()

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(asctime)s %(funcName)s(%(lineno)d) %(message)s')
    # ch.setFormatter(formatter)
    app_log = logging.getLogger("tornado.application")
    tornado.log.enable_pretty_logging()
    # app_log.addHandler(ch)
    logfile = os.path.abspath("websocket_app.log")
    # Rotate log after reaching 512K, keep 5 old copies.
    rotateHandler = RotatingFileHandler(logfile, "a", 512 * 1024, 10)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    rotateHandler.setFormatter(formatter)
    app_log.addHandler(rotateHandler)

    access_log = logging.getLogger("tornado.access")
    tornado.log.enable_pretty_logging()
    logfile2 = os.path.abspath("websocket_access.log")
    rotateHandler2 = RotatingFileHandler(logfile2, "a", 512 * 1024, 10)
    formatter2 = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    rotateHandler2.setFormatter(formatter2)
    access_log.addHandler(rotateHandler2)

    app_log.warning("Testnet: {}".format(is_testnet))

    if os.name == "posix":
        process = psutil.Process()
        limit = process.rlimit(psutil.RLIMIT_NOFILE)
        app_log.info("OS File limits {}, {}".format(limit[0], limit[1]))
        if limit[0] < 1024:
            app_log.error("Too small ulimit, please tune your system.")
            sys.exit()
    else:
        process = None

    app_log.info("Websocket Server {} Starting on port {}.".format(__version__, options.port))

    start_server(options.port)
