#! /usr/bin/env python3

import argparse
from lib import json_rpc


if __name__ == '__main__':
    
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(prog='pyrpcwallet', description='Lightweight Json RPC wallet')
    
    parser.add_argument('--rpc-host', help='the host to provide the JSON-RPC API (default: localhost)', 
                                      default='localhost')
    
    parser.add_argument('--rpc-port', type=int, 
                                      help='port on which to provide the JSON-RPC API (default: 8383)', 
                                      default="8383")
    
    parser.add_argument('--rpc-user', help='required username to use the JSON-RPC API via HTTP basic auth (default: bitcoinrpc)', 
                                      default="bitcoinrpc")
    
    parser.add_argument('--rpc-password', help='required password (for rpc-user) to use the JSON-RPC API via HTTP basic auth (default: "")', 
                                          default="")
    
    parser.add_argument('--database', help='database file path (default: wallet.db)', 
                                      default='wallet.db')

    parser.add_argument('--update-interval', type=int,
                                             help='interval in minutes for updating balances and unspent outputs from blockchain.info. 0 for manual update with updatebalances command (default: 10).',
                                             default=10)

    args = parser.parse_args()

    json_rpc.run_server(host=args.rpc_host, port=args.rpc_port, 
                        user=args.rpc_user, password=args.rpc_password, 
                        database=args.database,
                        update_interval=args.update_interval)