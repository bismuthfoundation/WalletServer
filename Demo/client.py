from bismuthclient.bismuthclient import BismuthClient
from tornado.options import define, options


if __name__ == '__main__':
    define("ip", default='127.0.0.1', help="Server IP to connect to, default 127.0.0.1")
    define("port", default=8150, help="Server port to connect to, default 8150")
    define("address", default='0634b5046b1e2b6a69006280fbe91951d5bb5604c6f469baa2bcd840', help="Address to test")
    define("verbose", default=False, help="verbose")
    options.parse_command_line()

    client = BismuthClient(wallet_file='wallet.der', servers_list=["{}:{}".format(options.ip, options.port)])

    """
    balance = client.command('balanceget', [options.address])
    print(balance)
    """

    """
    balance = client.command('balanceget', ['86cbc69e9f8522c58f5c97fd13e7a5634ea6012207984c54bf83fc7d'])
    print(balance)
    """

    # use with address 86cbc69e9f8522c58f5c97fd13e7a5634ea6012207984c54bf83fc7d
    """
    listop = client.command('addlistopfromjson', [options.address, 'dragg:sell'])
    print(listop)

    listopdata = client.command('listexactopdatajson', ['dragg:sell', 'ZeZC9bRDjpFKyYyJHLcLo7fDiizv:*:25'])
    print(listopdata)
    """

    """
    balance = client.command('globalbalanceget', [['0634b5046b1e2b6a69006280fbe91951d5bb5604c6f469baa2bcd840',
                                                   '86cbc69e9f8522c58f5c97fd13e7a5634ea6012207984c54bf83fc7d']])
    print(balance)
    """

    test = client.command('XTRA_test1', [])
    print(test)

