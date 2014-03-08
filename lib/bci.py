import requests, json
from pycoin.encoding import h2b
from .tx_script import TxScript
from .raw_transaction import RawTransaction
from pycoin.convention import satoshi_to_btc

class BCI():

    # TODO: max X addresses, else request by chunks
    @staticmethod
    def listunspent(addresses):
        try:
            response = requests.get("http://blockchain.info/unspent?active=" + "|".join(addresses))
           
            if response.status_code == 500 and response.text.lower() == "no free outputs to spend":
                return None, None
            elif response.status_code != 200:
                raise Exception("Bad status code returned from blockchain.info: %s" % response.status_code)
            unspent_outputs = response.json()['unspent_outputs']

        except requests.exceptions.RequestException as e:
            raise Exception("Problem getting unspent transactions from blockchain.info: %s" % e)

        #take the returned data to a format compatible with bitcoind's output
        listunspent = []
        for output in unspent_outputs:
            
            output['tx_hash'] = output['tx_hash'][::-1] #reverse string
            output['tx_hash'] = ''.join([output['tx_hash'][i:i+2][::-1] for i in range(0, len(output['tx_hash']), 2)]) #flip the character pairs within the string
            
            script = TxScript(h2b(output['script']))

            listunspent.append({
                'address': script.bitcoin_address_for_script(),
                'txid': output['tx_hash'],
                'vout': output['tx_output_n'],
                'scriptPubKey': output['script'],
                'amount': float(satoshi_to_btc(output['value'])),
                'confirmations': output['confirmations']
            })

        return listunspent
            
    @staticmethod
    def getblockcount():       
        try:
            response = requests.get("http://blockchain.info/q/getblockcount")
            if response.status_code != 200:
                raise Exception("Bad status code returned from blockchain.info: %s" % response.status_code)
            return int(response.text)
        except requests.exceptions.RequestException as e:
            raise Exception("Problem getting block count from blockchain.info: " % e)


    @staticmethod
    def getrawtransaction(tx_hash, verbose=0):
        try:
            response = requests.get("http://blockchain.info/rawtx/"+tx_hash+"?format=hex")
            
            if response.status_code != 200:
                raise Exception("Bad status code returned from blockchain.info: %s" % response.status_code)
            elif response.text.lower()=='invalid transaction hash':
                raise Exception("Invalid Transaction Hash: %s" % tx_hash)

            if verbose==1:
                unsigned_tx = RawTransaction(response.text)
                return unsigned_tx.to_json(return_dict=True)
            return response.text

        except requests.exceptions.RequestException as e:
            raise Exception("Problem getting raw transaction from blockchain.info: %s" % e)


    @staticmethod
    def getblock(block_hash):
        try:
            response = requests.get("http://blockchain.info/rawblock/"+block_hash)
            if response.status_code != 200:
                raise Exception("Bad status code returned from blockchain.info: %s" % response.status_code)
            elif response.text.lower()=='invalid block hash':
                raise Exception("Invalid Block Hash: %s" % tx_hash)

            bci_block = response.json()
            bictoind_block = {
                "hash" : bci_block['hash'],
                "size" : bci_block['size'],
                "height" : bci_block['height'],
                "version" : bci_block['ver'],
                "merkleroot" : bci_block['mrkl_root'],            
                "time" : bci_block['time'],
                "nonce" : bci_block['nonce'],
                "bits" : bci_block['bits'],
                "previousblockhash" : bci_block['prev_block'],
                "tx" : []
            }
            for tx in bci_block['tx']:
                #tx['hash'] = tx['hash'][::-1] #reverse string
                #tx['hash'] = ''.join([tx['hash'][i:i+2][::-1] for i in range(0, len(tx['hash']), 2)]) #flip the character pairs within the string
            
                bictoind_block['tx'].append(tx['hash'])

            return bictoind_block

        except requests.exceptions.RequestException as e:
            raise Exception("Problem getting block from blockchain.info: " % e)


    @staticmethod
    def getblockhash(height):

        try:
            # we really need a blockexplorer class ?
            response = requests.get("http://blockexplorer.com//q/getblockhash/"+str(height))
            if response.status_code != 200:
                raise Exception("Bad status code returned from blockexplorer.com: %s" % response.status_code)
            elif response.text.lower()=='error: block not found':
                raise Exception("Invalid Block Height: %s" % height)

            return response.text

        except requests.exceptions.RequestException as e:
            raise Exception("Problem getting block hash from blockexplorer.com: " % e)


    # TODO: max X addresses, else request by chunks
    @staticmethod
    def getbalance(addresses):
        try:
            response = requests.get("http://blockchain.info/fr/q/addressbalance/" + "|".join(addresses))
           
            if response.status_code != 200:
                raise Exception("Bad status code returned from blockchain.info: %s" % response.status_code)
            
            return int(response.text)
        except requests.exceptions.RequestException as e:
            raise Exception("Problem getting unspent transactions from blockchain.info: %s" % e)


    @staticmethod
    def sendrawtransaction(tx_hex):
        data = {'tx': tx_hex}
        try:
            response = requests.post("http://blockchain.info/pushtx", data=payload)
            # TODO: check response
            return response.text

        except requests.exceptions.RequestException as e:
            raise Exception("Problem sending raw transaction to blockchain.info: %s" % e)



