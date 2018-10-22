import connections
import socks
import json
import urllib3
import socket

def convert_ip_port(ip, some_port):
    """
    Get ip and port, but extract port from ip if ip was as ip:port
    :param ip:
    :param some_port: default port
    :return: (ip, port)
    """
    if ':' in ip:
        ip, some_port = ip.split(':')
    return ip, some_port
    
light_ip = ["wallet.bismuthplatform.de:7150","wallet.bismuth.online:8150","wallet1.bismuth.online:8150","bismuth.live:8150", "testnet2828.bismuthplatform.de:8150"]
port = 7150
ws_stats=[]
heights={}
backup_height = False

for address in light_ip:
            
    result_collection={} 
    ip, local_port = convert_ip_port(address, port)
    #app_log.info("Asking {}:{}".format(ip, local_port))
    print("Asking {}:{}".format(ip, local_port))
    try:
        s = socks.socksocket()
        s.settimeout(3)
        #connect to wallet-server and get statusjson info
        s.connect((ip, int(local_port)))
        connections.send(s, "statusjson", 10)
        result = connections.receive(s, 10)
        heights[address] = result.get("blocks")
        connections.send(s, "wstatusget", 10)
        result_ws = connections.receive(s, 10)
        clients = result_ws.get('clients')
        max_clients = 500
        last_active = result.get("server_timestamp")
    except Exception as e:
        clients = "unknown"
        last_active = "unknown"
        max_clients = "unknown"
        heights[address] = 0
        #app_log.info("WalletServer {}:{} not answering".format(ip, local_port))
           
    http = urllib3.PoolManager()
    try:
        chainjson = http.request('GET', 'http://78.28.227.89/api/stats/latestblock')
        chain = json.loads(chainjson.data.decode('utf-8'))
        print(heights[address])
        if heights[address] < (int(chain.get("height")) - 10):
            active = False
        else:
            active = True
        
    except Exception as e:
        #app_log.warning("bismuth.online API not reachable, using back method for testing "active")
        backup_height = True
        active = "unknown"
        
    country = "NA"
    ip_addr = socket.gethostbyname(ip)
    result_collection.update({'label':address,'ip':ip_addr, 'port':local_port, 'active':active, 'clients':clients, 'total_slots':max_clients, 'last_active':last_active, 'country':country})
    ws_stats.append(result_collection)



if backup_height:
    max_height = max(heights.values())
    for key in heights:
        listindex = [i for i,x in enumerate(heights) if x == key]
        if heights.get(key) < (max_height - 10):
            ws_stats[listindex[0]]['active'] = False
        else:
            ws_stats[listindex[0]]['active'] = True

else:
    pass    
print(ws_stats)  
with open('legacy.json', 'w') as file:  
    json.dump(ws_stats, file)  
