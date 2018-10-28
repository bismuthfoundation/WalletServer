"""
ws2json.py

Tests a list of official wallet servers, and produces the json output needed by the official API.

To be run by a cron everty 5 minutes.
"""

import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import connections
import socks
import urllib3
from tornado.ioloop import IOLoop
from tornado.websocket import websocket_connect

__version__ = '0.0.2'

# global vars come first - if need to be globals, then use UPPERCASE

# List of wallet servers ip or ip:port to test
# TODO: load from json with a helper function (separate code from data)
WALLET_SERVERS = []
WEBSOCKET_SERVERS = ['194.19.235.82:8155', "wallet.bismuthplatform.de:8155","testnet2828.bismuthplatform.de:8155"]
# TODO
WEBSOCKET_SERVERS = []
# Default port to use if none is provided
DEFAULT_PORT = 8150

DO_LEGACY = True
DO_WEBSOCKET = False

# variable to have zero terminal output, but one notice if something with level warning happened or not
global WARN

# Then functions


def convert_ip_port(ip, some_port=DEFAULT_PORT):
    """
    Get ip and port, but extract port from ip if ip was as ip:port
    :param ip:
    :param some_port: default port
    :return: (ip, port)
    """
    if ':' in ip:
        ip, some_port = ip.split(':')
    # since we have a function, make it returns the right type from the start
    return ip, int(some_port)


def test_legacy_server(a_server_dict, the_network_height=False):
    """
    Takes a server dict, the current network height if known and updates the dict with merged info
    {'label':address,'ip':ip_addr, 'port':local_port, 'active':active, 'clients':clients, 'total_slots':max_clients, 'last_active':last_active, 'country':country}
    """
    global WARN

    label = a_server_dict['label']
    app_log.info("Asking {}:{}".format(a_server_dict['ip'], a_server_dict['port']))
    #print("Asking {}:{}".format(ip, port))
    active = True  # Active by default
    try:
        s = socks.socksocket()
        s.settimeout(30)
        # connect to wallet-server and get statusjson info
        s.connect((a_server_dict['ip'], int(a_server_dict['port'])))
        connections.send(s, "statusget")
        result = connections.receive(s)
        a_server_dict['height'] = result[5]
        if the_network_height and a_server_dict['height'] < the_network_height - 10:
            # we have a reference, and we are late.
            #print("{} is too late: {} vs {}".format(an_address, HEIGHTS[address], the_network_height))
            app_log.warning("{} is too late: {} vs {}".format(label, a_server_dict['height'], the_network_height))
            WARN = True
            active = False
        connections.send(s, "wstatusget")
        result_ws = connections.receive(s)
        print(result_ws)
        clients = result_ws['clients']
        max_clients = result_ws.get('max_clients', 100)
        last_active = result_ws.get("server_timestamp", 0)
    except Exception as e:
        # prefer error values of the same type as expected values
        #print("Exception {} querying {}".format(e, an_address))
        clients = -1
        last_active = 0
        max_clients = -1
        a_server_dict['height'] = 0
        active = False
        app_log.warning("Exception {} querying {}".format(e, label))
        WARN = True
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        app_log.error('detail {} {} {}'.format(exc_type, fname, exc_tb.tb_lineno))

    a_server_dict['active'] = active
    a_server_dict['clients'] = clients
    a_server_dict['total_slots'] = max_clients
    a_server_dict['last_active'] = last_active


async def async_websocket_command(URL, command):
    """Async command get from websocket"""
    ws = await websocket_connect(URL)
    await ws.write_message(command)
    msg = await ws.read_message()
    return msg


def websocket_command(URL, command):
    """Sync version of the ws command get. convert async to sync"""
    return IOLoop.current().run_sync(lambda: async_websocket_command(URL, command))


def test_websocket_server(a_server_dict, the_network_height=False):
    """
    Takes a server dict, the current network height if known and updates the dict with merged info
    {'label':address,'ip':ip_addr, 'port':local_port, 'active':active, 'clients':clients, 'total_slots':max_clients, 'last_active':last_active, 'country':country}
    """
    global WARN

    label = a_server_dict['label']
    URL = "ws://{}:{}/web-socket/".format(a_server_dict['ip'], a_server_dict['port'])
    print("Testing {}".format(URL))
    resultjson = websocket_command(URL, '["statusjson"]')
    result = json.loads(resultjson)
    active = True  # Active by default
    # connect to wallet-server and get statusjson info
    if result:
        a_server_dict['height'] = result["blocks"]
        last_active = result["server_timestamp"]
    else:
        print("Connection closed")
        app_log.warning("Connection to {} closed, statusjson not received".format(label))
        last_active = 0
        a_server_dict['height'] = 0
        active = False
        WARN = True
    if the_network_height and a_server_dict['height'] < the_network_height - 10:
        # we have a reference, and we are late.
        app_log.warning("{} is too late: {} vs {}".format(label, a_server_dict['height'], the_network_height))
        WARN = True
        active = False
    """
    result_ws_json = websocket_command(URL,'["wstatusget"]')
    result_ws = json.loads(result_ws_json)
    print(result_ws)
    if result_ws:
        app_log.info("Connection to {} closed and everything is received".format(label))
        #clients = result_ws[0].get('clients')
    else:
        print("Connection closed")
        app_log.warning("Connection to {} closed, wstatusget not received".format(label))
        clients = -1
        max_clients = -1
        active = False
        WARN = True
    """
    # TODO
    max_clients = 500
    clients = 250
    country = "N/A"
    # Fill in extra info
    a_server_dict['active'] = active
    a_server_dict['clients'] = clients
    a_server_dict['total_slots'] = max_clients
    a_server_dict['last_active'] = last_active


def get_network_height():
    """
    Returns the network height from bismuth.online API.
    Returns False if the API was not available.
    """
    global WARN

    http = urllib3.PoolManager()
    try:
        chainjson = http.request('GET', 'http://bismuth.online/api/stats/latestblock')
        chain = json.loads(chainjson.data.decode('utf-8'))
        height = int(chain["height"])
        app_log.info("Bismuth.online API says network height is {}".format(height))
        return height

    except Exception as e:
        app_log.warning("bismuth.online API not reachable, using back method for testing active")
        WARN = True
        return False


# Main code comes at the end, after
if __name__ == "__main__":

    WARN = False

    app_log = logging.getLogger("wallet_api")
    app_log.setLevel(logging.INFO)
    logfile = os.path.abspath("jsonapi.log")
    # Rotate log after reaching 512K, keep 2 old copies.
    rotateHandler = RotatingFileHandler(logfile, "a", 512 * 1024, 2)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    rotateHandler.setFormatter(formatter)
    app_log.addHandler(rotateHandler)

    # This part is what goes on console.
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(funcName)s(%(lineno)d) %(message)s')
    ch.setFormatter(formatter)
    app_log.addHandler(ch)


# Try to get network height from API
    network_height = get_network_height()

    if DO_LEGACY:
        with open('../data/servers_wallet_legacy.json', 'r') as f:
            WALLET_SERVERS = json.load(f)

        for server in WALLET_SERVERS:
            # prefer several small functions to one long code
            test_legacy_server(server, network_height)
            # this will also allow to run one test per thread later on, instead of in sequence
        if not network_height:
            # The API was not responding, use fallback method to inactivate late servers
            max_height = max([server['height'] for server in WALLET_SERVERS])
            for server in WALLET_SERVERS:
                if server['height'] < max_height - 10:
                    server['active'] = False

    if DO_WEBSOCKET:
        for server in WEBSOCKET_SERVERS:
            test_websocket_server(server, network_height)
        if not network_height:
            # The API was not responding, use fallback method to inactivate late servers
            max_height = max([server['height'] for server in WEBSOCKET_SERVERS])
            for server in WEBSOCKET_SERVERS:
                if server['height'] < max_height - 10:
                    server['active'] = False


    if WARN:
        print("There are warnings, pls see jsonapi.log for details")
    else:
        print("no Warnings occured, to see Infos, open jsonapi.log")

    if DO_LEGACY:
        with open('../servers/wallet/legacy.json', 'w') as file:
            json.dump(WALLET_SERVERS, file)

    if DO_WEBSOCKET:
        with open('../servers/wallet/websocket.json', 'w') as file:
            json.dump(WEBSOCKET_SERVERS, file)
