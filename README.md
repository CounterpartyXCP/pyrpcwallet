pyrpcwallet
==========

Lightweigt JSON RPC wallet compatible with bitcoind

* same commands and same result as bitcoind JSON-RPC API
* no need to download the blockchain
* usable as a python library to develop your own wallet
* usable as command line wallet (without json-rpc)
* private keys are crypted with the same algorithm as wallet.dat
* sqlite database easyly usable with all languages and commmand line client
* and off course compatible with counterpartyd

# Changelog

* v0.1

# installation

<pre>
brew update
brew install sqlite

pip3 install bottle pycoin pycrypto

pip3 install https://github.com/rogerbinns/apsw/archive/master.zip

git clone https://github.com/JahPowerBit/pyrpcwallet.git

cd pyrpcwallet

</pre>

# Usage

<pre>
pyrpcwallet [-h] [--rpc-host RPC_HOST] [--rpc-port RPC_PORT]
                   [--rpc-user RPC_USER] [--rpc-password RPC_PASSWORD]
                   [--database DATABASE] [--update-interval UPDATE_INTERVAL]

Lightweight Json RPC wallet

optional arguments:
  -h, --help            show this help message and exit
  --rpc-host RPC_HOST   the host to provide the JSON-RPC API (default:
                        localhost)
  --rpc-port RPC_PORT   port on which to provide the JSON-RPC API (default:
                        8383)
  --rpc-user RPC_USER   required username to use the JSON-RPC API via HTTP
                        basic auth (default: bitcoinrpc)
  --rpc-password RPC_PASSWORD
                        required password (for rpc-user) to use the JSON-RPC
                        API via HTTP basic auth (default: "")
  --database DATABASE   database file path (default: wallet.db)
  --update-interval UPDATE_INTERVAL
                        interval in minutes for updating balances and unspent
                        outputs from blockchain.info. 0 for manual update with
                        updatebalances command (default: 10).
</pre>

# Available commands

<b>bitcoind commands</b>

+ getinfo (return only unlock_until)
+ walletpassphrase
+ listaddressgroupings
+ getbalance
+ listunspent
+ getnewaddress
+ validateaddress
+ dumpprivkey
+ decoderawtransaction
+ signrawtransaction
+ sendrawtransaction
+ getrawtransaction
+ getblockcount
+ getblockhash
+ getblock

https://en.bitcoin.it/wiki/Original_Bitcoin_client/API_calls_list

<b>additional commands</b>

+ updatebalances : retrieve from blockchain.info balances and unspent outputs. Use this command if you run pyrpcwallet with --update-interval=0

# Todo

+ command line client withtout json rpc server
+ functionnals test to compare result from bitcoind and pyrpcwallet
+ BIP32 features
+ add followings commands:
	* addmultisigaddress
	* backupwallet
	* createmultisig
	* getdifficulty
	* getrawchangeaddress
	* getreceivedbyaddress
	* gettransaction
	* listreceivedbyaddress
	* listtransactions
	* sendfrom
	* sendmany
	* sendtoaddress
	* settxfee
	* signmessage
	* verifymessage
	* walletlock
	* walletpassphrasechange

# License

The MIT License (MIT)

Copyright (c) 2014 by JahPowerBit

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.