import binascii, os, random, json

bytes_from_int = chr if bytes == str else lambda x: bytes([x])

def b2h(b):
    return binascii.hexlify(b).decode('utf-8')


def random_hex(length):
    return binascii.b2a_hex(os.urandom(length))


class JsonDecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o,  decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)




