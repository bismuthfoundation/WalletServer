"""
Node interface class for both wallet server (tcp) and websocket wallet server
"""

import json
import time
import datetime
from inspect import signature
from tornado.tcpclient import TCPClient
import tornado
import tornado.gen
import tornado.iostream


from modules.helpers import *


__version_ = '0.0.7'


# TODO: factorize all commands that are sent "as is" to the local node.

TX_KEYS = ["block_height", "timestamp", "address", "recipient", "amount", "signature", "public_key", "block_hash", "fee", "reward", "operation", "openfield"]


def method_params_count(func):
    return len(signature(func).parameters)


class NodeInterface():

    def __init__(self, mempool, ledger, config):
        self.mempool = mempool
        self.ledger = ledger
        self.cache = {}
        self.config = config
        # print(getattr(self,"cached"))
        # print(self.__dict__)
        # print(locals())
        self.user_method_list = {func: method_params_count(getattr(self, func)) for func in dir(self)
                            if callable(getattr(self, func)) and func.startswith("user_")}
        self.admin_method_list = {}
        # print(user_method_list)

    def param_count_of(self, method_name, rights):
        """
        returns the number of expected params for this command.
        returns -1 if the rights do not fit or unknown command
        """
        if 'user_' + method_name in self.user_method_list:
            return self.user_method_list['user_' + method_name]
        if 'admin' in rights and 'admin_' + method_name in self.admin_method_list:
            return self.admin_method_list['admin_' + method_name]
        # No function or no right
        return -1

    async def call_user(self, args):
        method_name = args.pop(0)
        result = await getattr(self, "user_" + method_name)(*args)
        return result

    def cached(self, key, timeout=30):
        if key in self.cache:
            if self.cache[key][0] > time.time() - timeout:
                return True
        return False

    def set_cache(self, key, value):
        self.cache[key] = (time.time(), value)

    async def _node_stream(self):
        return await TCPClient().connect(self.config.node_ip, self.config.node_port)

    async def _receive(self, stream):
        """
        Get a command, async version
        :param stream:
        :param ip:
        :return:
        """
        header = await tornado.gen.with_timeout(datetime.timedelta(seconds=35), stream.read_bytes(10),
                                                quiet_exceptions=tornado.iostream.StreamClosedError)
        data_len = int(header)
        data = await tornado.gen.with_timeout(datetime.timedelta(seconds=10), stream.read_bytes(data_len),
                                              quiet_exceptions=tornado.iostream.StreamClosedError)
        data = json.loads(data.decode("utf-8"))
        return data

    async def _send(self, data, stream):
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
            app_log.error("send_to_stream {}".format(str(e)))
            raise

    async def user_statusget(self):
        # don't hammer the node, cache recent info
        if self.cached("status"):
            return self.cache['status'][1]
        stream = None
        try:
            # too old, ask the node
            # TODO: factorize all the node forwarding methods
            stream = await self._node_stream()
            try:
                await self._send("statusget", stream)
                res = await self._receive(stream)
                self.set_cache("status", res)
                return res
            except KeyboardInterrupt:
                stream.close()
        except Exception as e:
            print(e)
            # print(CONFIG.node_ip, CONFIG.node_port)
        finally:
            if stream:
                stream.close()

    async def user_statusjson(self):
        # don't hammer the node, cache recent info
        if self.cached("statusjson"):
            return self.cache['statusjson'][1]
        stream = None
        try:
            stream = await self._node_stream()
            try:
                await self._send("statusjson", stream)
                res = await self._receive(stream)
                self.set_cache("statusjson", res)
                return res
            except KeyboardInterrupt:
                stream.close()
        except Exception as e:
            print(e)
        finally:
            if stream:
                stream.close()

    async def user_diffget(self):
        node_status = await self.user_statusget()
        return node_status[8]

    async def user_aliasesget(self, addresses):
        # TODO: local cache of Addresses / Aliases => todo in the wallet ?.
        stream = await self._node_stream()
        try:
            await self._send("aliasesget", stream)
            await self._send(addresses, stream)
            res = await self._receive(stream)
            return res
        except KeyboardInterrupt:
            stream.close()
        finally:
            if stream:
                stream.close()

    async def user_addfromalias(self, alias_resolve):
        # TODO: cache
        stream = await self._node_stream()
        try:
            await self._send("addfromalias", stream)
            await self._send(alias_resolve, stream)
            res = await self._receive(stream)
            return res
        except KeyboardInterrupt:
            stream.close()
        finally:
            if stream:
                stream.close()

    async def user_aliascheck(self, alias_desired):
        stream = await self._node_stream()
        try:
            await self._send("aliascheck", stream)
            await self._send(alias_desired, stream)
            res = await self._receive(stream)
            return res
        except KeyboardInterrupt:
            stream.close()
        finally:
            if stream:
                stream.close()

    async def user_aliasget(self, address):
        # TODO: cache
        stream = await self._node_stream()
        try:
            await self._send("aliasget", stream)
            await self._send(address, stream)
            res = await self._receive(stream)
            return res
        except KeyboardInterrupt:
            stream.close()
        finally:
            if stream:
                stream.close()

    async def user_tokensget(self, address):
        stream = await self._node_stream()
        try:
            await self._send("tokensget", stream)
            await self._send(address, stream)
            res = await self._receive(stream)
            return res
        except KeyboardInterrupt:
            stream.close()
        finally:
            if stream:
                stream.close()

    async def user_mpinsert(self, mp_insert):
        # TODO: factorize with node_aliases above
        stream = await self._node_stream()
        try:
            await self._send("mpinsert", stream)
            await self._send(mp_insert, stream)
            res = await self._receive(stream)
            return res
        except KeyboardInterrupt:
            stream.close()
        finally:
            if stream:
                stream.close()

    async def user_blocklast(self):
        if self.cached("blocklast", 30):
            return self.cache['blocklast'][1]
        if self.config.direct_ledger:
            last = await self.ledger.async_fetchone("SELECT * FROM transactions WHERE reward > 0 ORDER BY block_height DESC LIMIT 1")
        else:
            stream = await self._node_stream()
            try:
                await self._send("blocklast", stream)
                last = await self._receive(stream)
            except KeyboardInterrupt:
                stream.close()
            finally:
                if stream:
                    stream.close()
        self.set_cache("blocklast", last)
        return last

    async def user_mpget(self):
        if self.cached("mpget", 30):
            return self.cache['mpget'][1]
        # too old, really get
        mp = await self.mempool.async_fetchall('SELECT * FROM transactions ORDER BY amount DESC')
        self.set_cache("mpget", mp)
        return mp

    async def user_mpgetjson(self):
        mp = await self.user_mpget()
        return [dict(zip(TX_KEYS, tx)) for tx in mp]

    async def user_txget(self, transaction_id, addresses=[]):
        # TODO: this is intensive. rate limit or cache, but needs a garbage collector in cache function then.
        """
        if self.cached("txget", 10):
            return self.cache['txget'][1]
        """
        if len(transaction_id) == 2:
            transaction_id, addresses = transaction_id
        if self.config.direct_ledger:
            if len(addresses):
                recipients = json.dumps(addresses).replace("[","(").replace(']',')')
                tx = await self.ledger.async_fetchone("SELECT * FROM transactions WHERE recipient IN {} AND signature LIKE ?"
                                                      .format(recipients),
                                                      (transaction_id + '%',))
            else:
                tx = await self.ledger.async_fetchone("SELECT * FROM transactions WHERE signature like ?",
                                                      (transaction_id + '%',))
        else:
            stream = await self._node_stream()
            try:
                await self._send("txget", stream)
                await self._send(transaction_id, stream)
                tx = await self._receive(stream)
            except KeyboardInterrupt:
                stream.close()
            finally:
                if stream:
                    stream.close()
        if tx:
            return tx
        else:
            return ["Ko", "No such TxId"]

    async def user_txgetjson(self, transaction_id, addresses=[]):
        tx = await self.user_txget(transaction_id, addresses)
        if len(tx) == 2:
            # error
            return tx
        return dict(zip(TX_KEYS, tx))

    async def user_annverget(self):
        if self.cached("annverget", 60*10):
            return self.cache['annverget'][1]
        ann_ver = ''
        if self.config.direct_ledger:
            ann_addr = self.config.genesis_conf
            result = await self.ledger.async_fetchone("SELECT openfield FROM transactions "
                                                      "WHERE address = ? AND openfield LIKE ? "
                                                      "ORDER BY block_height DESC limit 1",
                                                      (ann_addr, "annver=%"))
            ann_ver = replace_regex(result[0], "annver=")
        else:
            stream = await self._node_stream()
            try:
                await self._send("annverget", stream)
                ann_ver = await self._receive(stream)
            except KeyboardInterrupt:
                stream.close()
            finally:
                if stream:
                    stream.close()
        self.set_cache("annverget", ann_ver)
        return ann_ver

    # TODO: review this param thing.
    async def user_addlistlim(self, address, limit=10):
        offset = 0
        if len(address) == 3:
            address, limit, offset = address
        elif len(address) == 2:
            address, limit = address
        txs = []
        if self.config.direct_ledger:
            txs = await self.ledger.async_fetchall("SELECT * FROM transactions WHERE (address = ? OR recipient = ?) "
                                                   "ORDER BY block_height DESC LIMIT ?, ?",
                                                   (address, address, offset, limit))
        else:
            stream = await self._node_stream()
            try:
                await self._send("addlistlim", stream)
                await self._send(address, stream)
                await self._send(limit, stream)
                txs = await self._receive(stream)
            except KeyboardInterrupt:
                stream.close()
            finally:
                if stream:
                    stream.close()
        return txs

    async def user_addlistlimfrom(self, address, limit=10, offset=0):

        if len(address) == 3:
            address, limit, offset = address
        elif len(address) == 2:
            address, limit = address
        txs = []
        if self.config.direct_ledger:
            txs = await self.ledger.async_fetchall("SELECT * FROM transactions WHERE (address = ? OR recipient = ?) "
                                                   "ORDER BY block_height DESC LIMIT ?, ?",
                                                   (address, address, offset, limit))
        else:
            stream = await self._node_stream()
            try:
                await self._send("addlistlim", stream)
                await self._send(address, stream)
                await self._send(limit, stream)
                txs = await self._receive(stream)
            except KeyboardInterrupt:
                stream.close()
            finally:
                if stream:
                    stream.close()
        return txs

    async def user_addlistlimjson(self, address, limit=10):
        txs = await self.user_addlistlim(address, limit)
        return [dict(zip(TX_KEYS, tx)) for tx in txs]

    async def user_addlistlimfromjson(self, address, limit=10, offset=0):
        txs = await self.user_addlistlimfrom(address, limit, offset)
        return [dict(zip(TX_KEYS, tx)) for tx in txs]

    async def user_addlist(self, address):
        if self.config.direct_ledger:
            txs = await self.ledger.async_fetchall("SELECT * FROM transactions WHERE (address = ? OR recipient = ?) "
                                                   "ORDER BY block_height DESC",
                                                   (address, address))
        else:
            stream = await self._node_stream()
            try:
                await self._send("addlist", stream)
                await self._send(address, stream)
                txs = await self._receive(stream)
            except KeyboardInterrupt:
                stream.close()
            finally:
                if stream:
                    stream.close()
        return txs

    async def user_annget(self):
        # TODO: factorize with annverget
        if self.cached("annget", 60*10):
            return self.cache['annget'][1]
        ann_addr = self.config.genesis_conf
        ann = ''
        if self.config.direct_ledger:
            result = await self.ledger.async_fetchone("SELECT openfield FROM transactions "
                                                      "WHERE address = ? AND openfield LIKE ? "
                                                      "ORDER BY block_height DESC limit 1",
                                                      (ann_addr, "ann=%"))
            ann = replace_regex(result[0], "ann=")
        else:
            stream = await self._node_stream()
            try:
                await self._send("annget", stream)
                ann = await self._receive(stream)
            except KeyboardInterrupt:
                stream.close()
            finally:
                if stream:
                    stream.close()
        self.set_cache("annget", ann)
        return ann

    async def user_balanceget(self, balance_address):
        if self.config.direct_ledger:
            base_mempool = await self.mempool.async_fetchall("SELECT amount, openfield, operation FROM transactions "
                                                             "WHERE address = ?;",
                                               (balance_address,))
            # include mempool fees
            debit_mempool = 0
            if base_mempool:
                for x in base_mempool:
                    debit_tx = Decimal(x[0])
                    fee = fee_calculate(x[1], x[2], 700001)
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
        else:
            stream = await self._node_stream()
            try:
                await self._send("balanceget", stream)
                await self._send(balance_address, stream)
                balance = await self._receive(stream)
                return balance
            except KeyboardInterrupt:
                stream.close()
            finally:
                if stream:
                    stream.close()

    async def user_balancegetjson(self, balance_address):
        values = await self.user_balanceget(balance_address)
        keys = ["balance", "total_credits", "total_debits", "total_fees", "total_rewards", "balance_no_mempool"]
        return dict(zip(keys, values))
