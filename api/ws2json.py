"""
ws2json.py

Tests a list of official wallet servers, and produces the json output needed by the official API.

To be run by a cron everty 5 minutes.
"""

import os
import json
import socket
import logging
from logging.handlers import RotatingFileHandler


import connections
import socks
import urllib3

# global vars come first - if need to be globals, then use UPPERCASE

# List of wallet servers ip or ip:port to test
# TODO: load from json with a helper function (separate code from data)
LIGHT_IP = ["wallet.bismuthplatform.de:7150","wallet.bismuth.online:8150","wallet1.bismuth.online:8150","bismuth.live:8150", "testnet2828.bismuthplatform.de:8150"]
# Default port to use if none is provided
DEFAULT_PORT = 8150

# a dict to lookup height of a given ip:port
HEIGHTS = {}

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


def test_legacy_server(an_address, the_network_height=False):
    """
    Takes an ip:port string, the current network height if known and returns a qualified
    {'label':address,'ip':ip_addr, 'port':local_port, 'active':active, 'clients':clients, 'total_slots':max_clients, 'last_active':last_active, 'country':country}
    dict
    """
    global WARN
    
    ip, port = convert_ip_port(an_address)
    app_log.info("Asking {}:{}".format(ip, port))
    #print("Asking {}:{}".format(ip, port))
    active = True  # Active by default
    try:
        s = socks.socksocket()
        s.settimeout(3)
        # connect to wallet-server and get statusjson info
        s.connect((ip, port))
        connections.send(s, "statusjson", 10)
        result = connections.receive(s, 10)
        HEIGHTS[address] = result.get("blocks")
        if the_network_height and HEIGHTS[address] < the_network_height - 10:
            # we have a reference, and we are late.
            #print("{} is too late: {} vs {}".format(an_address, HEIGHTS[address], the_network_height))
            app_log.warning("{} is too late: {} vs {}".format(an_address, HEIGHTS[address], the_network_height))
            WARN = True
            active = False
        connections.send(s, "wstatusget", 10)
        result_ws = connections.receive(s, 10)
        clients = result_ws.get('clients')
        max_clients = 500
        last_active = result.get("server_timestamp")
    except Exception as e:
        # prefer error values of the same type as expected values
        #print("Exception {} querying {}".format(e, an_address))
        clients = -1
        last_active = 0
        max_clients = -1
        HEIGHTS[address] = 0
        active = False
        app_log.warning("Exception {} querying {}".format(e, an_address))
        WARN = True

    country = "N/A"
    ip_addr = socket.gethostbyname(ip)
    return {'label': address, 'ip': ip_addr, 'port': port, 'active': active, 'clients': clients,
            'total_slots': max_clients, 'last_active': last_active, 'country': country}


def get_network_height():
    """
    Returns the network height from bismuth.online API.
    Returns False if the API was not available.
    """
    global WARN
    
    http = urllib3.PoolManager()
    try:
        chainjson = http.request('GET', 'http://78.28.227.89/api/stats/latestblock')
        chain = json.loads(chainjson.data.decode('utf-8'))
        height = int(chain["height"])
        #print("Bismuth.online API says network height is {}".format(height))
        app_log.info("Bismuth.online API says network height is {}".format(height))
        return height

    except Exception as e:
        #print("bismuth.online API not reachable, using back method for testing active")
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
    
    # Try to get network height from API
    network_height = get_network_height()

    # prefer explicit names to abbrev.
    wallets_stats = []
    for address in LIGHT_IP:
        # prefer several small functions to one long code
        test_result = test_legacy_server(address, network_height)
        # this will also allow to run one test per thread later on, instead of in sequence.
        wallets_stats.append(test_result)

    if not network_height:
        # The API was not responding, use fallback method to inactivate late servers
        # This could go into a function as well
        max_height = max(HEIGHTS.values())
        for key in HEIGHTS:
            listindex = [i for i,x in enumerate(HEIGHTS) if x == key]
            if HEIGHTS.get(key) < (max_height - 10):
                wallets_stats[listindex[0]]['active'] = False
            else:
                wallets_stats[listindex[0]]['active'] = True

    else:
        pass
    
    if WARN:
        print("There are warnings, pls see jsonapi.log for details")
    else:
        print("no Warnings occured, to see Infos, open jsonapi.log")

    with open('legacy.json', 'w') as file:
        json.dump(wallets_stats, file)
