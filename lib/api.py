from lib.wallet import Wallet
from lib.bci import BCI


class API():

    wallet_actions = ["listaddressgroupings", "getbalance", "listunspent", "getnewaddress", "importprivkey",
                      "validateaddress", "dumpprivkey", "signrawtransaction", "decoderawtransaction", "updatebalances",
                      "dumppubkey"]

    bci_actions = ["sendrawtransaction", "getrawtransaction", "getblockcount", "getblockhash", "getblock"]

    def __init__(self, passphrase, config):
        self.config = config
        self.passphrase = passphrase
        self.wallet = Wallet(self.passphrase, self.config)

    def do(self, action, params=[]):
        result = ''
        if action in API.wallet_actions:
            method = getattr(self.wallet, action)
            return method(*params)
        elif action in API.bci_actions:
            method = getattr(BCI, action)
            return method(*params)
        else:
            raise Exception('Unknown action')


