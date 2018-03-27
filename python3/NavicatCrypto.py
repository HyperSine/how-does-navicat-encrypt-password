import blowfish
import hashlib
from Crypto.Cipher import AES

def XorBytes(a: bytes, b: bytes):
    if type(a) is not bytes or type(b) is not bytes:
        raise TypeError('Either a or b is not a bytes.')
    if len(a) != len(b):
        raise ValueError('a and b do not have the same length.')
    return bytes([a[i] ^ b[i] for i in range(0, len(a))])

PKCS7Padding = lambda data, block_size : data + (block_size - len(data) % block_size) * bytes([block_size - len(data) % block_size])
PKCS7Unpadding = lambda data : data[0:-data[-1]]

def XorBytesByLength(a : bytes, b : bytes, length : int):
    if type(a) is not bytes or type(b) is not bytes:
        raise TypeError('Either a or b is not a bytes.')
    if type(length) is not int:
        raise TypeError('Parameter length must be a int.')

    if length <= 0:
        raise ValueError('Parameter length must be larger than 0.')
    if len(a) < length:
        raise ValueError('The length of a must be larger than parameter length.')
    if len(b) < length:
        raise ValueError('The length of b must be larger than parameter length.')

    return bytes([a[i] ^ b[i] for i in range(0, length)])


class Navicat11Crypto:

    def __init__(self, key = b'3DC5CA39'):
        self.Key = hashlib.sha1(key).digest()
        self.Cipher = blowfish.Cipher(self.Key)
        self.IV = self.Cipher.encrypt_block(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')

    def EncryptString(self, s : str):
        if type(s) != str:
            raise TypeError('Parameter s must be str.')

        inData = s.encode()
        CurVector = bytes(self.IV)
        Round = len(inData) // 8
        Result = b''

        for i in range(0, Round):
            temp = XorBytes(inData[8 * i:8 * i + 8], CurVector)
            temp = self.Cipher.encrypt_block(temp)
            CurVector = XorBytes(CurVector, temp)
            Result += temp

        LeftLength = len(inData) % 8
        if LeftLength != 0:
            CurVector = self.Cipher.encrypt_block(CurVector)
            Result += XorBytesByLength(inData[8 * Round:8 * Round + LeftLength], CurVector, LeftLength)

        return Result.hex().upper()

    def DecryptString(self, s : str):
        if type(s) != str:
            raise TypeError('Parameter s must be str.')

        inData = bytes.fromhex(s)
        CurVector = bytes(self.IV)
        Round = len(inData) // 8
        Result = b''

        for i in range(0, Round):
            temp = self.Cipher.decrypt_block(inData[8 * i:8 * i + 8])
            temp = XorBytes(temp, CurVector)
            Result += temp
            CurVector = XorBytes(CurVector, inData[8 * i:8 * i + 8])

        LeftLength = len(inData) % 8
        if LeftLength != 0:
            CurVector = self.Cipher.encrypt_block(CurVector)
            Result += XorBytesByLength(inData[8 * Round:8 * Round + LeftLength], CurVector, LeftLength)

        return Result.decode()

class Navicat12Crypto(Navicat11Crypto):

    def __init__(self):
        super(Navicat12Crypto, self).__init__()


    def EncryptStringForNCX(self, s : str):
        AESCipher = AES.new(b'libcckeylibcckey', AES.MODE_CBC, iv=b'libcciv libcciv ')
        return AESCipher.encrypt(PKCS7Padding(s.encode(), AESCipher.block_size)).hex().upper()

    def DecryptStringForNCX(self, s : str):
        AESCipher = AES.new(b'libcckeylibcckey', AES.MODE_CBC, iv=b'libcciv libcciv ')
        return PKCS7Unpadding(AESCipher.decrypt(bytes.fromhex(s))).decode()
