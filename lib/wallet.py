import os, appdirs, random

from pycoin.wallet import Wallet as PycoinWallet
from pycoin import ecdsa
from pycoin.encoding import public_pair_to_bitcoin_address, wif_to_secret_exponent, is_valid_bitcoin_address, secret_exponent_to_wif
from pycoin.convention import satoshi_to_btc, btc_to_satoshi

from .utils import random_hex
from .wallet_crypter import WalletCrypter
from .raw_transaction import RawTransaction
from .secret_exponent_solver import SecretExponentSolver
from .wallet_db import WalletDB

from decimal import Decimal as D


class Wallet():

    def __init__(self, passphrase, dbpath):
        self.passphrase = passphrase.encode('utf8')
        self.crypter = WalletCrypter()
        self.db = WalletDB(dbpath)
        


    def encryptsecretexponent(self, secret_exponent):
        self.checkpassphrase()
        salt = random_hex(16)
        rounds = int(50000+random.random()*20000)
        self.crypter.set_passphrase(self.passphrase, salt, rounds)
        encrypted_secret_exponent = str(self.crypter.encrypt(secret_exponent))
        return encrypted_secret_exponent, rounds, salt


    def decryptsecretexponent(self, encrypted_secret_exponent, rounds, salt):
        try:
            self.crypter.set_passphrase(self.passphrase, salt, rounds)
            secret_exponent = self.crypter.decrypt(eval(encrypted_secret_exponent))
            secret_exponent = int(secret_exponent, 16)
            return secret_exponent
        except:
            raise Exception("Invalid passphrase")

    def getsecretexponent(self, address):
        if is_valid_bitcoin_address(address)==False:
            raise Exception("Invalid address: %s" % address)

        address, encrypted_secret_exponent, rounds, salt = self.db.getaddress(address)
        if encrypted_secret_exponent is not None:
            return self.decryptsecretexponent(encrypted_secret_exponent, rounds, salt)

        raise Exception("Unknown address: %s" % address)


    def checkpassphrase(self):
        if self.passphrase=='':
            raise Exception("Invalid passphrase")
        # a random address is verified. todo: Maybe give the ability to have different passphrase for each address?
        address, encrypted_secret_exponent, rounds, salt = self.db.getoneaddress()
        if address is None:
            return True #first use
            
        self.decryptsecretexponent(encrypted_secret_exponent, rounds, salt)
        return True


    def insertaddress(self, address, secret_exponent):
        encrypted_secret_exponent, rounds, salt = self.encryptsecretexponent(secret_exponent)
        self.db.insertaddress(address, encrypted_secret_exponent, rounds, salt)      


    def getnewaddress(self, seed=""):
        if seed=="":
            seed = os.urandom(64)
        else:
            seed = seed.encode("utf8")
        entropy = bytearray(seed)
        pycwallet = PycoinWallet.from_master_secret(bytes(entropy), is_test=False)
        address = pycwallet.bitcoin_address()
        secret_exponent = hex(self.secret_exponent)[2:].encode('utf8')
        self.insertaddress(address, secret_exponent)
        return address


    def importprivkey(self, wif):
        secret_exponent = wif_to_secret_exponent(wif) 
        public_pair = ecdsa.public_pair_for_secret_exponent(ecdsa.generator_secp256k1, secret_exponent)
        address = public_pair_to_bitcoin_address(public_pair)
        secret_exponent = hex(secret_exponent)[2:].encode('utf8')
        self.insertaddress(address, secret_exponent)
        return address


    def dumpprivkey(self, address, return_sec_exp=False):
        if is_valid_bitcoin_address(address)==False:
            return Exception("Invalid address %s" % address)
        try:
            secret_exponent = self.getsecretexponent(address)
            wif = secret_exponent_to_wif(secret_exponent)
        except:
            raise Exception("Unknown address: %s" % address)
        return wif


    def validateaddress(self, address):
        infos = {
            "isvalid": is_valid_bitcoin_address(address)
        }
        if infos["isvalid"]:
            infos["address"] = address
            infos["ismine"] = False
            address, encrypted_secret_exponent, rounds, salt = self.db.getaddress(address)
            if address is not None:
                infos["ismine"] = True
        return infos;


    def signrawtransaction(self, unsigned_hex):
        unsigned_tx = RawTransaction(unsigned_hex)
        solver = SecretExponentSolver(self)
        tx_hex = unsigned_tx.sign(solver)
        return tx_hex


    def decoderawtransaction(self, unsigned_hex):
        unsigned_tx = RawTransaction(unsigned_hex)
        return unsigned_tx.to_json(pretty=True)


    def updatebalances(self):
        self.db.update();
        return self.getbalance()


    def listunspent(self, update=False):
        if update:
            self.updatebalances()
        return self.db.listunspent()


    def listaddressgroupings(self):
        listaddress = []
        addresses = self.db.getalladdresses()
        for address in addresses:
            listaddress.append([address['address'], float(satoshi_to_btc(address['balance']))])
        return [listaddress]

    def getbalance(self):
        balance = D('0')
        addresses = self.db.getalladdresses()
        for address in addresses:
            balance = balance + satoshi_to_btc(address['balance'])
        return float(balance)



