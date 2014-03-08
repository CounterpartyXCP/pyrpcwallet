import os, apsw, time

from lib.bci import BCI
from pycoin.convention import satoshi_to_btc, btc_to_satoshi

class WalletDB():

    def __init__(self, dbpath):
        self.db = apsw.Connection(dbpath)
        cursor = self.db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS addresses (
                          address TEXT,
                          secret_exponent TEXT,
                          rounds INTEGER,
                          salt TEXT,
                          created_at INTEGER,
                          balance INTEGER,
                          balance_at INTEGER,
                          balance_source TEXT,
                          PRIMARY KEY (address))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS unspents (
                          address TEXT,
                          txid TEXT,
                          scriptPubKey TEXT,
                          amount INTEGER  ,
                          vout INTEGER,
                          confirmations INTEGER,
                          updated_at INTEGER,
                          source TEXT,
                          PRIMARY KEY (txid))''')
        cursor.execute('''CREATE INDEX IF NOT EXISTS
                          unspents_address_idx ON unspents (address)''')


    def insertaddress(self, address, encrypted_secret_exponent, rounds, salt):
        cursor = self.db.cursor()
        sql = 'INSERT INTO addresses (address, secret_exponent, rounds, salt, created_at) VALUES (?,?,?,?,?)'
        values = (address, encrypted_secret_exponent, rounds, salt, int(time.time()))
        cursor.execute(sql, values)


    def getaddress(self, address):
        cursor = self.db.cursor()
        sql = 'SELECT address, secret_exponent, rounds, salt FROM addresses WHERE address=?'
        for address, encrypted_secret_exponent, rounds, salt in cursor.execute(sql, [address]):
            return address, encrypted_secret_exponent, rounds, salt           
        return None, None, None, None

    def getoneaddress(self):
        cursor = self.db.cursor()
        sql = 'SELECT address, secret_exponent, rounds, salt FROM addresses LIMIT 1'
        for address, encrypted_secret_exponent, rounds, salt in cursor.execute(sql):
            return address, encrypted_secret_exponent, rounds, salt           
        return None, None, None, None

    def getalladdresses(self):
        addresses = []
        cursor = self.db.cursor()
        sql = 'SELECT address, balance FROM addresses'
        for address, balance in cursor.execute(sql):
            addresses.append({"address": address, "balance": balance})
        return addresses


    # update all balances and unspents from BCI
    def update(self):
        cursor = self.db.cursor()
        addresses = self.getalladdresses()
        for address in addresses:
            bci_balance = BCI.getbalance([address['address']])
            if bci_balance!=address['balance']:
                now = int(time.time())

                sql = 'UPDATE addresses SET balance=?, balance_at=?, balance_source=? WHERE address=?'
                values = (bci_balance, now, 'blockchain.info', address['address'])
                cursor.execute(sql, values)

                new_unspents = BCI.listunspent([address['address']])
                # Make this in sql transaction even unspents are outdated ??
                cursor.execute("DELETE FROM unspents WHERE address=?", (address['address'],)) 
                if len(new_unspents)>0:
                    values = []
                    for new_unspent in new_unspents:
                        values.append([
                            address['address'],
                            new_unspent['txid'],
                            new_unspent['scriptPubKey'],
                            btc_to_satoshi(new_unspent['amount']),
                            new_unspent['vout'],
                            new_unspent['confirmations'],
                            now,
                            'blockchain.info',
                        ])
                    sql = '''INSERT INTO unspents (address, txid, scriptPubKey, amount, vout, confirmations, updated_at, source)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
                    cursor.executemany(sql, values)


    def listunspent(self):
        cursor = self.db.cursor()
        sql = "SELECT address, txid, scriptPubKey, amount, vout, confirmations, updated_at, source FROM unspents ORDER BY address"
        unspents = []
        for unspent in cursor.execute(sql):      
            unspents.append({
                'address': unspent[0], 
                'txid': unspent[1],
                'scriptPubKey': unspent[2], 
                'amount': float(satoshi_to_btc(unspent[3])), 
                'vout': unspent[4], 
                'confirmations': unspent[5], 
                'updated_at': unspent[6], 
                'source': unspent[7]
            })
        return unspents







