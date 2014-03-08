import json, time
from lib.utils import JsonDecimalEncoder
from lib.api import API
from lib.wallet_db import WalletDB
from threading import Timer, Thread
import bottle
from bottle import route, Bottle, request, error, response, auth_basic
import logging

app = Bottle()

def check_auth(user, passwd):
    if user==config.RPC_USER and passwd==config.RPC_PASSWORD:
        return True
    return False


class RPCConfig:
    RPC_USER = ''
    RPC_PASSWORD = ''
    PASSPHRASE = ''
    DATABASE = ''
    UNLOCKED_UNTIL = 0
    UPDATE_INTERVAL = 10


config = RPCConfig()


def delete_passphrase():
    config.PASSPHRASE = ''
    config.UNLOCKED_UNTIL = 0
    print("passphrase expired", time.time())


def set_passphrase(passphrase, expiration=60.0):
    config.PASSPHRASE = passphrase
    config.UNLOCKED_UNTIL = int(time.time())+int(expiration)
    print("wallet unlocked for %s seconds" % str(expiration), time.time())
    eraser = Timer(float(expiration), delete_passphrase)
    eraser.start()
    return None


def get_infos():
    return {
        "unlocked_until": config.UNLOCKED_UNTIL
    }
    

def update_balances():
    db = WalletDB(config.DATABASE)
    while True:   
        print("Updating balances and unspent outputs from Blockchain.info...")     
        db.update()
        print("Balances updated")
        time.sleep(int(config.UPDATE_INTERVAL*60))


@app.post('/')
@auth_basic(check_auth)
def rpc():
    payload = bottle.request.json
    method = None
    result = {}
    try:     
        action = payload['method']
        result['id'] = payload['id'] 
        if action == 'walletpassphrase':
            result['result'] = set_passphrase(*payload['params'])
        elif action == 'getinfo':
            result['result'] = get_infos()
        else:
            api = API(config.PASSPHRASE, config.DATABASE)     
            result['result'] = api.do(action, payload['params'])
        result['error'] = None 
    except Exception as e:
        result['result'] = None
        result['error'] = str(e)
    return json.dumps(result, cls=JsonDecimalEncoder)


def run_server(host='localhost', port=8448, user='rpcuser', password='', database='wallet.db', update_interval=10):
    config.RPC_USER = user
    config.RPC_PASSWORD = password
    config.DATABASE = database
    config.UPDATE_INTERVAL = update_interval

    if update_interval>0:
        updater = Thread(target=update_balances)
        updater.daemon = True
        updater.start()

    app.run(host=host, port=port)

