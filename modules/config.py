
import os.path as path

__version__ = '0.0.3'


class Get:

    # "param_name":["type"] or "param_name"=["type","property_name"]
    vars={
        "port":["str"],
        "websocket_port":["str"],
        "node_port":["str"],
        "max_clients":["int"],
        "testnet":["bool"],
        "debug":["bool"],
        "node_path":["str"],
        "db_path":["str"],
        "debug_level":["str"],
        "allowed":["str"],
        "banlist":["list"],
        "whitelist":["list"],
        "direct_ledger": ["bool"]
    }

    # Optional default values so we don't bug if they are not in the config.
    # For compatibility
    defaults = {
        "port": 8150,
        "websocket_port": 8155,
        "node_port": 5658,
        "node_path": "../Bismuth",
        "db_path": "../Bismuth/static",
        "debug": False,
        "testnet": False,
        "max_clients": 50,
        "direct_ledger": True

    }

    def load_file(self,filename):
        #print("Loading",filename)
        for line in open(filename):
            if '=' in line:
                left,right = map(str.strip,line.rstrip("\n").split("="))
                if not left in self.vars:
                    # Warn for unknown param?
                    continue
                params = self.vars[left]
                if params[0] == "int":
                    right = int(right)
                elif params[0] == "list":
                    right = [item.strip() for item in right.split(",")]
                elif params[0] == "bool":
                    if right.lower() in ["false", "0", "", "no"]:
                        right = False
                    else:
                        right = True

                else:
                    # treat as "str"
                    pass
                if len(params)>1:
                    # deal with properties that do not match the config name.
                    left = params[1]
                setattr(self,left,right)
        for key, default in self.defaults.items():
            if key not in self.__dict__:
                setattr(self, key, default)

        self.node_ip = "127.0.0.1"
        self.genesis_conf = "4edadac9093d9326ee4b17f869b14f1a2534f96f9c5d7b48dc9acaed"
        # print(self.__dict__)

    def read(self):
        # first of all, load from default config so we have all needed params
        self.load_file("config.txt")
        # then override with optional custom config
        if path.exists("config_custom.txt"):
            self.load_file("config_custom.txt")
