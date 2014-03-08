import binascii

from pycoin import ecdsa
from pycoin.encoding import public_pair_to_sec, is_sec_compressed, sec_to_public_pair,\
    hash160_sec_to_bitcoin_address, public_pair_to_bitcoin_address,\
    public_pair_to_hash160_sec

from pycoin.tx.script import der, opcodes, tools

from .utils import bytes_from_int
from .tx_script import TxScript
from .exceptions import SolvingError

class SecretExponentSolver(object):

    def __init__(self, wallet):
        self.wallet = wallet

    def __call__(self, tx_out_script, signature_hash, signature_type):
        """Figure out how to create a signature for the incoming transaction, and sign it.

        tx_out_script: the tx_out script that needs to be "solved"
        signature_hash: the bignum hash value of the new transaction reassigning the coins
        signature_type: always SIGHASH_ALL (1)
        """

        if signature_hash == 0:
            raise SolvingError("signature_hash can't be 0")

        tx_script = TxScript(tx_out_script)
        opcode_value_list = tx_script.match_script_to_templates()

        ba = bytearray()

        compressed = True
        for opcode, v in opcode_value_list:
            if opcode == opcodes.OP_PUBKEY:
                public_pair = sec_to_public_pair(v)
                bitcoin_address = public_pair_to_bitcoin_address(public_pair, compressed=compressed)
            elif opcode == opcodes.OP_PUBKEYHASH:
                bitcoin_address = hash160_sec_to_bitcoin_address(v)
            else:
                raise SolvingError("can't determine how to sign this script")
           
            secret_exponent = self.wallet.getsecretexponent(bitcoin_address)

            r,s = ecdsa.sign(ecdsa.generator_secp256k1, secret_exponent, signature_hash)
            sig = der.sigencode_der(r, s) + bytes_from_int(signature_type)
            ba += tools.compile(binascii.hexlify(sig).decode("utf8"))
            if opcode == opcodes.OP_PUBKEYHASH:
                public_pair = ecdsa.public_pair_for_secret_exponent(ecdsa.generator_secp256k1, secret_exponent)
                ba += tools.compile(binascii.hexlify(public_pair_to_sec(public_pair, compressed=compressed)).decode("utf8"))

        return bytes(ba)
