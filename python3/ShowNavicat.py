#!/usr/bin/env python3
import platform

if platform.system().lower() != 'windows':
    print('Please run this script in Windows.')
    exit(-1)

import sys, winreg
from Crypto.Hash import SHA1
from Crypto.Cipher import AES, Blowfish

#
# Navicat12Crypto is not needed
#
class Navicat11Crypto:

    @staticmethod
    def _XorBytes(a : bytes, b : bytes):
        return bytes([ i ^ j for i, j in zip(a, b) ])

    def __init__(self, Key = b'3DC5CA39'):
        self._CipherKey = SHA1.new(Key).digest()
        self._Cipher = Blowfish.new(self._CipherKey, Blowfish.MODE_ECB)
        self._IV = self._Cipher.encrypt(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')

    def EncryptString(self, s : str):
        if type(s) != str:
            raise TypeError('Parameter s must be a str.')
        else:
            plaintext = s.encode('utf-8')
            ciphertext = b''
            cv = self._IV
            full_round, left_length = divmod(len(plaintext), 8)

            for i in range(0, full_round * 8, 8):
                t = Navicat11Crypto._XorBytes(plaintext[i:i + 8], cv)
                t = self._Cipher.encrypt(t)
                cv = Navicat11Crypto._XorBytes(cv, t)
                ciphertext += t
            
            if left_length != 0:
                cv = self._Cipher.encrypt(cv)
                ciphertext += Navicat11Crypto._XorBytes(plaintext[8 * full_round:], cv[:left_length])

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
                t = Navicat11Crypto._XorBytes(t, cv)
                plaintext += t
                cv = Navicat11Crypto._XorBytes(cv, ciphertext[i:i + 8])
            
            if left_length != 0:
                cv = self._Cipher.encrypt(cv)
                plaintext += Navicat11Crypto._XorBytes(ciphertext[8 * full_round:], cv[:left_length])
            
            return plaintext.decode('utf-8')

NavicatCipher = Navicat11Crypto()
ServersTypes = {
    'MySQL Server' : 'Software\\PremiumSoft\\Navicat\\Servers',
    'MariaDB Server' : 'Software\\PremiumSoft\\NavicatMARIADB\\Servers',
    'MongoDB Server' : 'Software\\PremiumSoft\\NavicatMONGODB\\Servers',
    'MSSQL Server' : 'Software\\PremiumSoft\\NavicatMSSQL\\Servers',
    'OracleSQL Server' : 'Software\\PremiumSoft\\NavicatOra\\Servers',
    'PostgreSQL Server' : 'Software\\PremiumSoft\\NavicatPG\\Servers',
    # 'SQLite Server' : 'Software\\PremiumSoft\\NavicatSQLite\\Servers'
}

for ServersTypeName, ServersRegistryPath in ServersTypes.items():
    print('+--------------------------------------------------+')
    print('|%s|' % ServersTypeName.center(50))
    print('+--------------------------------------------------+')

    try:
        ServersRegistryKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, ServersRegistryPath)
    except OSError:
        print('')
        print('No servers is found.')
        print('')
        continue

    i = 0
    try:
        while True:
            print('')

            ServerName = winreg.EnumKey(ServersRegistryKey, i)
            ServerRegistryKey = winreg.OpenKey(ServersRegistryKey, ServerName)

            try:
                ServerHost = winreg.QueryValueEx(ServerRegistryKey, 'Host')[0]
                ServerPort = winreg.QueryValueEx(ServerRegistryKey, 'Port')[0]
                if ServersTypeName == 'OracleSQL Server':
                    ServerInitialDb = winreg.QueryValueEx(ServerRegistryKey, 'InitialDatabase')[0]
                else:
                    ServerInitialDb = None
                ServerUsername = winreg.QueryValueEx(ServerRegistryKey, 'Username')[0]
                ServerPassword = winreg.QueryValueEx(ServerRegistryKey, 'Pwd')[0]
                if len(ServerPassword) != 0:
                    ServerPassword = NavicatCipher.DecryptString(ServerPassword)

                ServerUseSsh = winreg.QueryValueEx(ServerRegistryKey, 'UseSSH')[0]
                if ServerUseSsh != 0:
                    ServerSshHost = winreg.QueryValueEx(ServerRegistryKey, 'SSH_Host')[0]
                    ServerSshPort = winreg.QueryValueEx(ServerRegistryKey, 'SSH_Port')[0]
                    ServerSshUsername = winreg.QueryValueEx(ServerRegistryKey, 'SSH_Username')[0]
                    ServerSshPassword = winreg.QueryValueEx(ServerRegistryKey, 'SSH_Password')[0]
                    if len(ServerSshPassword) != 0:
                        ServerSshPassword = NavicatCipher.DecryptString(ServerSshPassword)
                else:
                    ServerSshHost = None
                    ServerSshPort = None
                    ServerSshUsername = None
                    ServerSshPassword = None

                print('%-18s' % 'ServerName:', ServerName)
                print('%-18s' % 'Host:', ServerHost)
                print('%-18s' % 'Port:', ServerPort)
                if ServerInitialDb != None:
                    print('%-18s' % 'InitialDatabase:', ServerInitialDb)
                print('%-18s' % 'Username:', ServerUsername)
                print('%-18s' % 'Password:', ServerPassword)
                if ServerUseSsh:
                    print('%-18s' % 'SSH Host:', ServerSshHost)
                    print('%-18s' % 'SSH Port:', ServerSshPort)
                    print('%-18s' % 'SSH Username:', ServerSshUsername)
                    print('%-18s' % 'SSH Password:', ServerSshPassword)
            except:
                print('[-] Failed to get info about server "%s". Server info may be corrupted.' % ServerName, file = sys.stderr)

            winreg.CloseKey(ServerRegistryKey)
            i += 1
    except OSError:
        if i == 0:
            print('No servers is found.')
            print('')
        continue

    winreg.CloseKey(ServersRegistryKey)

