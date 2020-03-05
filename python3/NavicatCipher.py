#!/usr/bin/env python3
import sys
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
        padded_plaintext = Padding.pad(s.encode('ascii'), AES.block_size, style = 'pkcs7')
        return cipher.encrypt(padded_plaintext).hex().upper()

    def DecryptStringForNCX(self, s : str):
        cipher = AES.new(b'libcckeylibcckey', AES.MODE_CBC, iv = b'libcciv libcciv ')
        padded_plaintext = cipher.decrypt(bytes.fromhex(s))
        return Padding.unpad(padded_plaintext, AES.block_size, style = 'pkcs7').decode('ascii')

if __name__ == '__main__':

    def Help():
        print('Usage:')
        print('    NavicatCrypto.py <enc|dec> [-ncx] <plaintext|ciphertext>')
        print('')
        print('        <enc|dec>                "enc" for encryption, "dec" for decryption.')
        print('                                 This parameter must be specified.')
        print('')
        print('        [-ncx]                   Indicate that plaintext/ciphertext is')
        print('                                 prepared for/exported from NCX file.')
        print('                                 This parameter is optional.')
        print('')
        print('        <plaintext|ciphertext>   Plaintext string or ciphertext string.')
        print('                                 NOTICE: Ciphertext string must be a hex string.')
        print('                                 This parameter must be specified.')
        print('')

    def Main(argc : int, argv : list):
        if argc == 3:
            if argv[1].lower() == 'enc':
                print(Navicat11Crypto().EncryptString(argv[2]))
            elif argv[1].lower() == 'dec':
                print(Navicat11Crypto().DecryptString(argv[2]))
            else:
                Help()
                return -1
        elif argc == 4:
            if argv[1].lower() == 'enc' and argv[2].lower() == '-ncx':
                print(Navicat12Crypto().EncryptStringForNCX(argv[3]))
            elif argv[1].lower() == 'dec' and argv[2].lower() == '-ncx':
                print(Navicat12Crypto().DecryptStringForNCX(argv[3]))
            else:
                Help()
                return -1
        else:
            Help()
        
        return 0

    exit(Main(len(sys.argv), sys.argv))

