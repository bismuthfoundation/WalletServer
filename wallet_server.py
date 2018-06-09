"""
A Tornado based wallet server for Bismuth.
EggdraSyl - June 2018

Place these files in your bismuth directory. Needs core bismuth libs and config.

pip3 install -r wallet-server-requirements.txt
"""


import time
import sys
import os
import json
import logging
import asyncio
# from datetime import datetime
from logging.handlers import RotatingFileHandler
import aioprocessing
# Tornado
# from tornado import process
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.iostream import StreamClosedError
from tornado.tcpserver import TCPServer
import tornado.log
from tornado.tcpclient import TCPClient

# Bismuth specific modules
from sqlitebase import SqliteBase
import options as config
from ann import replace_regex
from quantizer import *
from essentials import fee_calculate

__version__ = '0.0.3'


# Limit can be pretty high, only one thread is used for the whole server.
MAX_CLIENTS = 500

# Port we're listening on
PORT = 8150


# Server
# -----------------------------------------------------------------------------

class WalletServer(TCPServer):
    """Tornado asynchronous TCP server."""
    clients = set()
    cache = {}
    mempool = None
    ledger = None

    async def handle_stream(self, stream, address):
        global access_log
        global app_log
        global stop_event
        global MAX_CLIENTS
        ip, fileno = address
        error_shown = False
        if len(self.clients) >= MAX_CLIENTS:
            access_log.info("Reached {} max clients, denying connection for {}.".format(MAX_CLIENTS, ip))
            return
        access_log.info("Incoming connection from " + ip)
        WalletServer.clients.add(address)
        while not stop_event.is_set():
            try:
                await self.command(stream, ip)
            except StreamClosedError:
                access_log.info("Client {} left.".format(address))
                error_shown = True
                WalletServer.clients.remove(address)
                break
            except ValueError:
                if options.verbose:
                    access_log.info("Client {} Rejected.".format(address))
                error_shown = True
                WalletServer.clients.remove(address)
                break
            except Exception as e:
                if not error_shown:
                    what = str(e)
                    if not 'OK' in what:
                        app_log.error("handle_stream {} for ip {}".format(what, ip))

    async def _receive(self, stream, ip):
        """
        Get a command, async version
        :param stream:
        :param ip:
        :return:
        """
        header = await stream.read_bytes(10)
        data_len = int(header)
        data = await stream.read_bytes(data_len)
        data = json.loads(data.decode("utf-8"))
        return data

    async def _send(self, data, stream, ip):
        """
        sends an object to the stream, async.
        :param data:
        :param stream:
        :param ip:
        :return:
        """
        global app_log
        try:
            data = str(json.dumps(data))
            header = str(len(data)).encode("utf-8").zfill(10)
            full = header + data.encode('utf-8')
            await stream.write(full)
        except Exception as e:
            app_log.error("send_to_stream {} for ip {}".format(str(e), ip))
            raise

    def cached(self, key, timeout=30):
        if key in self.cache:
            if self.cache[key][0] > time.time() - 30:
                return True
        return False

    def set_cache(self, key, value):
        self.cache[key] = (time.time(), value)

    async def command(self, stream, ip):
        global access_log
        data = await self._receive(stream, ip)
        if options.verbose:
            access_log.info("Command " + data)
        # "free commands"
        if data == "statusget":
            # Get from the node and forward
            node_status = await self.node_status(ip)
            await self._send(node_status, stream, ip)
            return
        if data == "balanceget":
            # Get address
            address = await self._receive(stream, ip)
            balance = await self.balanceget(address)
            await self._send(balance, stream, ip)
            return
        if data == "blocklast":
            blocklast = await self.blocklast(ip)
            await self._send(blocklast, stream, ip)
            return
        if data == "diffget":
            # cheat for wallet, use value from statusget, no need to do heavy calc again. is already in cache.
            node_status = await self.node_status(ip)
            diff = node_status[8]
            await self._send(diff, stream, ip)
            return
        if data == "mpget":
            mempool = await self.mpget(ip)
            await self._send(mempool, stream, ip)
            return
        if data == "annverget":
            ann_ver = await self.annverget(ip)
            await self._send(ann_ver, stream, ip)
            return
        if data == 'addlistlim':
            # Get address
            address = await self._receive(stream, ip)
            # Get lines count
            limit = await self._receive(stream, ip)
            txs = await self.ledger.async_fetchall("SELECT * FROM transactions WHERE (address = ? OR recipient = ?) ORDER BY block_height DESC LIMIT ?",
                                                 (address, address, limit))
            await self._send(txs, stream, ip)
            return
        if data == 'addlist':
            # Get address
            address = await self._receive(stream, ip)
            txs = await self.ledger.async_fetchall("SELECT * FROM transactions WHERE (address = ? OR recipient = ?) ORDER BY block_height DESC",
                                                 (address, address))
            await self._send(txs, stream, ip)
            return
        if data == "annget":
            ann = await self.annget(ip)
            await self._send(ann, stream, ip)
            return
        if data == "aliasesget":
            # since this triggers an alias reindex on the node, forward to the node. But maybe a simple query of the index would be enough if the node reindexes often enough.
            # Get addresses
            addresses = await self._receive(stream, ip)
            node_aliases = await self.node_aliases(addresses, ip)
            await self._send(node_aliases, stream, ip)
            return
        if data == "aliasget":
            # since this triggers an alias reindex on the node, forward to the node. But maybe a simple query of the index would be enough if the node reindexes often enough.
            # Get addresses
            address = await self._receive(stream, ip)
            node_alias = await self.node_alias(address, ip)
            await self._send(node_alias, stream, ip)
            return
        if data == "tokensget":
            # since this triggers an alias reindex on the node, forward to the node. But maybe a simple query of the index would be enough if the node reindexes often enough.
            # Get addresses
            address = await self._receive(stream, ip)
            node_tokens = await self.node_tokens(address, ip)
            await self._send(node_tokens, stream, ip)
            return
        if data == "mpinsert":
            mempool_insert = await self._receive(stream, ip)
            # since we don't want to dup too much code, let just forward to the node atm.
            mpinsert_result = await self.node_mpinsert(mempool_insert, ip)
            await self._send(mpinsert_result, stream, ip)
            return
        if data == "mpclear":
            # TODO: only for admin
            return

        # roles
        rights = await getrights(ip)
        # admin only
        if "admin" in rights:
            # TODO
            if data == 'status':
                return
            if data == 'setconfig':
                return

        raise ValueError("Unknown Command " + data)
        return

    async def node_status(self, ip):
        global CONFIG
        # don't hammer the node, cache recent info
        if self.cached("status"):
            return self.cache['status'][1]
        try:
            # too old, ask the node
            stream = await TCPClient().connect(CONFIG.node_ip_conf, CONFIG.port)
            try:
                await self._send("statusget", stream, ip)
                res = await self._receive(stream, ip)
                self.set_cache("status", res)
                return res
            except KeyboardInterrupt:
                stream.close()
        except Exception as e:
            print(e)
            # print(CONFIG.node_ip_conf, CONFIG.port)

    async def node_aliases(self, addresses, ip):
        global CONFIG
        stream = await TCPClient().connect(CONFIG.node_ip_conf, CONFIG.port)
        try:
            await self._send("aliasesget", stream, ip)
            await self._send(addresses, stream, ip)
            res = await self._receive(stream, ip)
            return res
        except KeyboardInterrupt:
            stream.close()

    async def node_alias(self, address, ip):
        global CONFIG
        stream = await TCPClient().connect(CONFIG.node_ip_conf, CONFIG.port)
        try:
            await self._send("aliasget", stream, ip)
            await self._send(address, stream, ip)
            res = await self._receive(stream, ip)
            return res
        except KeyboardInterrupt:
            stream.close()

    async def node_tokens(self, address, ip):
        global CONFIG
        stream = await TCPClient().connect(CONFIG.node_ip_conf, CONFIG.port)
        try:
            await self._send("tokensget", stream, ip)
            await self._send(address, stream, ip)
            res = await self._receive(stream, ip)
            return res
        except KeyboardInterrupt:
            stream.close()

    async def node_mpinsert(self, mp_insert, ip):
        # TODO: factorize with node_aliases above
        global CONFIG
        stream = await TCPClient().connect(CONFIG.node_ip_conf, CONFIG.port)
        try:
            await self._send("mpinsert", stream, ip)
            await self._send(mp_insert, stream, ip)
            res = await self._receive(stream, ip)
            return res
        except KeyboardInterrupt:
            stream.close()

    async def blocklast(self, ip):
        if self.cached("blocklast"):
            return self.cache['blocklast'][1]
        last = await self.ledger.async_fetchone("SELECT * FROM transactions WHERE reward > 0 ORDER BY block_height DESC LIMIT 1")
        self.set_cache("blocklast", last)
        return last

    async def mpget(self, ip):
        if self.cached("mpget", 10):
            return self.cache['mpget'][1]
        # too old, really get
        mp = await self.mempool.async_fetchall('SELECT * FROM transactions ORDER BY amount DESC')
        self.set_cache("mpget", mp)
        return mp

    async def annverget(self, ip):
        global CONFIG
        if self.cached("annverget", 60):
            return self.cache['annverget'][1]
        ann_addr = CONFIG.genesis_conf
        result = await self.ledger.async_fetchone("SELECT openfield FROM transactions WHERE address = ? AND openfield LIKE ? ORDER BY block_height DESC limit 1", (ann_addr, "annver=%"))
        ann_ver = replace_regex(result[0], "annver=")
        self.set_cache("annverget", ann_ver)
        return ann_ver

    async def annget(self, ip):
        # TODO: factorize with annverget
        global CONFIG
        if self.cached("annget", 60):
            return self.cache['annget'][1]
        ann_addr = CONFIG.genesis_conf
        result = await self.ledger.async_fetchone("SELECT openfield FROM transactions WHERE address = ? AND openfield LIKE ? ORDER BY block_height DESC limit 1", (ann_addr, "ann=%"))
        ann = replace_regex(result[0], "ann=")
        self.set_cache("annget", ann)
        return ann

    async def balanceget(self, balance_address):
        base_mempool = await self.mempool.async_fetchall("SELECT amount, openfield FROM transactions WHERE address = ?;",
                                           (balance_address,))
        # include mempool fees
        debit_mempool = 0
        if base_mempool:
            for x in base_mempool:
                debit_tx = Decimal(x[0])
                fee = fee_calculate(x[1])
                debit_mempool = quantize_eight(debit_mempool + debit_tx + fee)
        else:
            debit_mempool = 0
        # include mempool fees
        credit_ledger = Decimal("0")
        for entry in await self.ledger.async_execute("SELECT amount FROM transactions WHERE recipient = ?;", (balance_address,)):
            try:
                credit_ledger = quantize_eight(credit_ledger) + quantize_eight(entry[0])
                credit_ledger = 0 if credit_ledger is None else credit_ledger
            except:
                credit_ledger = 0

        fees = Decimal("0")
        debit_ledger = Decimal("0")

        for entry in await self.ledger.async_execute("SELECT fee, amount FROM transactions WHERE address = ?;", (balance_address,)):
            try:
                fees = quantize_eight(fees) + quantize_eight(entry[0])
                fees = 0 if fees is None else fees
            except:
                fees = 0
            try:
                debit_ledger = debit_ledger + Decimal(entry[1])
                debit_ledger = 0 if debit_ledger is None else debit_ledger
            except:
                debit_ledger = 0

        debit = quantize_eight(debit_ledger + debit_mempool)

        rewards = Decimal("0")
        for entry in await self.ledger.async_execute("SELECT reward FROM transactions WHERE recipient = ?;", (balance_address,)):
            try:
                rewards = quantize_eight(rewards) + quantize_eight(entry[0])
                rewards = 0 if rewards is None else rewards
            except:
                rewards = 0
        balance = quantize_eight(credit_ledger - debit - fees + rewards)
        balance_no_mempool = float(credit_ledger) - float(debit_ledger) - float(fees) + float(rewards)
        # app_log.info("Mempool: Projected transction address balance: " + str(balance))
        return str(balance), str(credit_ledger), str(debit), str(fees), str(rewards), str(balance_no_mempool)

    async def background(self):
        """
        This runs in a background coroutine and print out status
        :return:
        """
        global stop_event
        global app_log
        while not stop_event.is_set():
            try:
                app_log.info("STATUS: {} Connected clients.".format(len(self.clients)))
                await asyncio.sleep(30)
            except Exception as e:
                app_log.error("Error background {}".format(str(e)))
                #raise


async def getrights(ip):
    global app_log
    global CONFIG
    try:
        result = ['none']
        if ip in CONFIG.allowed_conf:
            result.append("admin")
        return result
    except Exception as e:
        app_log.warning("Error getrights {}".format(str(e)))


def start_server(port):
    global app_log
    global stop_event
    global PORT
    global CONFIG
    server = WalletServer()
    # attach mempool db
    server.mempool = SqliteBase(options.verbose, db_path='./', db_name='mempool.db', app_log=app_log)
    # attach ledger
    server.ledger = SqliteBase(options.verbose, db_path=CONFIG.ledger_path_conf, db_name='', app_log=app_log)
    #server.listen(port)
    server.bind(port)
    server.start(1)  # Force one process only
    if options.verbose:
        app_log.info("Starting server on tcp://localhost: {}".format(port))
    io_loop = IOLoop.instance()
    io_loop.spawn_callback(server.background)
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

    CONFIG = config.Get()
    CONFIG.read()
    version = CONFIG.version_conf
    if "testnet" in version:
        is_testnet = True
    else:
        is_testnet = False

    define("port", default=PORT, help="port to listen on")
    define("verbose", default=False, help="verbose")
    options.parse_command_line()

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
    logfile = os.path.abspath("wallet_app.log")
    # Rotate log after reaching 512K, keep 5 old copies.
    rotateHandler = RotatingFileHandler(logfile, "a", 512 * 1024, 10)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    rotateHandler.setFormatter(formatter)
    app_log.addHandler(rotateHandler)

    access_log = logging.getLogger("tornado.access")
    tornado.log.enable_pretty_logging()
    logfile2 = os.path.abspath("wallet_access.log")
    rotateHandler2 = RotatingFileHandler(logfile2, "a", 512 * 1024, 10)
    formatter2 = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    rotateHandler2.setFormatter(formatter2)
    access_log.addHandler(rotateHandler2)

    app_log.warning("Testnet: {}".format(is_testnet))

    app_log.info("Wallet Server {} Starting.".format(__version__))

    start_server(options.port)
