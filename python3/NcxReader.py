#!/usr/bin/env python3
import sys, xml.etree.ElementTree
from Crypto.Hash import SHA1
from Crypto.Cipher import AES, Blowfish
from Crypto.Util import strxor, Padding

class Navicat11Crypto:

    def __init__(self, Key = b'3DC5CA39'):
        self._Key = SHA1.new(Key).digest()
        self._Cipher = Blowfish.new(self._Key, Blowfish.MODE_ECB)
        self._IV = self._Cipher.encrypt(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')

    def EncryptString(self, s : str):
        if type(s) != str:
            raise TypeError('Parameter s must be a str.')
        else:
            plaintext = s.encode('ascii')
            ciphertext = b''
            cv = self._IV
            full_round, left_length = divmod(len(plaintext), 8)

            for i in range(0, full_round * 8, 8):
                t = strxor.strxor(plaintext[i:i + 8], cv)
                t = self._Cipher.encrypt(t)
                cv = strxor.strxor(cv, t)
                ciphertext += t
            
            if left_length != 0:
                cv = self._Cipher.encrypt(cv)
                ciphertext += strxor.strxor(plaintext[8 * full_round:], cv[:left_length])

            return ciphertext.hex().upper()

    def DecryptString(self, s : str):
        if type(s) != str:
            raise TypeError('Parameter s must be str.')
        else:
            plaintext = b''
            ciphertext = bytes.fromhex(s)
            cv = self._IV
            full_round, left_length = divmod(len(ciphertext), 8)

            for i in range(0, full_round * 8, 8):
                t = self._Cipher.decrypt(ciphertext[i:i + 8])
                t = strxor.strxor(t, cv)
                plaintext += t
                cv = strxor.strxor(cv, ciphertext[i:i + 8])
            
            if left_length != 0:
                cv = self._Cipher.encrypt(cv)
                plaintext += strxor.strxor(ciphertext[8 * full_round:], cv[:left_length])
            
            return plaintext.decode('ascii')

class Navicat12Crypto(Navicat11Crypto):

    def __init__(self):
        super().__init__()

    def EncryptStringForNCX(self, s : str):
        cipher = AES.new(b'libcckeylibcckey', AES.MODE_CBC, iv = b'libcciv libcciv ')
        padded_plaintext = Padding.pad(s.encode('ascii'), AES.block_size, stype = 'pkcs7')
        return cipher.encrypt(padded_plaintext).hex().upper()

    def DecryptStringForNCX(self, s : str):
        cipher = AES.new(b'libcckeylibcckey', AES.MODE_CBC, iv = b'libcciv libcciv ')
        padded_plaintext = cipher.decrypt(bytes.fromhex(s))
        return Padding.unpad(padded_plaintext, AES.block_size, style = 'pkcs7').decode('ascii')

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

def Help():
    print('Usage:')
    print('    NcxReader.py <Path to ncx file>')
    print()

def Main(argc : int, argv : list):
    if argc != 2:
        Help()
        return 0
    else:
        cipher = Navicat12Crypto()
        xmlFile = xml.etree.ElementTree.parse(argv[1])
        conns = xmlFile.getroot()
        for conn in conns:
            assert(conn.tag == 'Connection')

            print(conn.attrib['ConnectionName'].center(50, '-'))
            print('%-16s = %s' % ('Connection Type', conn.attrib['ConnType']))
            print('%-16s = %s' % ('Host', conn.attrib['Host']))
            print('%-16s = %s' % ('Port', conn.attrib['Port']))
            print('%-16s = %s' % ('UserName', conn.attrib['UserName']))
            print('%-16s = %s' % ('Password', TryDecrypt(cipher, conn.attrib['Password'])))

            if (conn.attrib['SSH'].lower() != 'false'):
                print('%-16s = %s' % ('SSH Host', conn.attrib['SSH_Host']))
                print('%-16s = %s' % ('SSH Port', conn.attrib['SSH_Port']))
                print('%-16s = %s' % ('SSH UserName', conn.attrib['SSH_UserName']))
                print('%-16s = %s' % ('SSH Password', TryDecrypt(cipher, conn.attrib['SSH_Password'])))
            print()

exit(Main(len(sys.argv), sys.argv))

