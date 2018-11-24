#!/usr/bin/env python3
import sys, xml.etree.ElementTree
from Crypto.Cipher import AES, Blowfish
from Crypto.Hash import SHA1

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


class Navicat11Crypto(object):

    def __init__(self, key = b'3DC5CA39'):
        self.Key = SHA1.new(key).digest()
        self.Cipher = Blowfish.new(self.Key, Blowfish.MODE_ECB)
        self.IV = self.Cipher.encrypt(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')

    def EncryptString(self, s : str):
        if type(s) != str:
            raise TypeError('Parameter s must be str.')

        inData = s.encode()
        CurVector = bytes(self.IV)
        Round = len(inData) // 8
        Result = b''

        for i in range(0, Round):
            temp = XorBytes(inData[8 * i:8 * i + 8], CurVector)
            temp = self.Cipher.encrypt(temp)
            CurVector = XorBytes(CurVector, temp)
            Result += temp

        LeftLength = len(inData) % 8
        if LeftLength != 0:
            CurVector = self.Cipher.encrypt(CurVector)
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
            temp = self.Cipher.decrypt(inData[8 * i:8 * i + 8])
            temp = XorBytes(temp, CurVector)
            Result += temp
            CurVector = XorBytes(CurVector, inData[8 * i:8 * i + 8])

        LeftLength = len(inData) % 8
        if LeftLength != 0:
            CurVector = self.Cipher.encrypt(CurVector)
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

def TryDecrypt(cipher, s):
    try:
        return cipher.DecryptString(s)
    except:
        pass

    try:
        return cipher.DecryptStringForNCX(s)
    except:
        pass
    
    raise ValueError('Decryption failed!')

def help():
    print('Usage:')
    print('    NcxReader.py <path to ncx file>')
    print()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        help()
        exit(0)

    cipher = Navicat12Crypto()
    xmlFile = xml.etree.ElementTree.parse(sys.argv[1])
    Connections = xmlFile.getroot()
    for Connection in Connections:
        assert(Connection.tag == 'Connection')

        print('-----%s-----' % Connection.attrib['ConnectionName'])
        print('%s = %s' % ('Connection Type', Connection.attrib['ConnType']))
        print('%s = %s' % ('Host', Connection.attrib['Host']))
        print('%s = %s' % ('Port', Connection.attrib['Port']))
        print('%s = %s' % ('UserName', Connection.attrib['UserName']))
        print('%s = %s' % ('Password', TryDecrypt(cipher, Connection.attrib['Password'])))

        if (Connection.attrib['SSH'].lower() != 'false'):
            print('%s = %s' % ('SSH Host', Connection.attrib['SSH_Host']))
            print('%s = %s' % ('SSH Port', Connection.attrib['SSH_Port']))
            print('%s = %s' % ('SSH UserName', Connection.attrib['SSH_UserName']))
            print('%s = %s' % ('SSH Password', TryDecrypt(cipher, Connection.attrib['SSH_Password'])))
        print()
else:
    print('Please run this script directly.')
