from Crypto.Cipher import AES
import random, hashlib, binascii


class WalletCrypter(object):
    def set_passphrase(self, passphrase, salt, rounds):
        data = passphrase + salt
        for i in range(rounds):
            data = hashlib.sha512(data).digest()
        self.set_key(data[0:32])
        self.set_IV(data[32:32+16])
        return len(data)

    def set_key(self, key):
        self.key = key

    def set_IV(self, iv):
        self.IV = iv[0:16]

    def encrypt(self, data):
        return AES.new(self.key, AES.MODE_CBC, self.IV).encrypt(data)

    def decrypt(self, data):
        return AES.new(self.key, AES.MODE_CBC, self.IV).decrypt(data)
