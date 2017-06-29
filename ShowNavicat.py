import winreg
from NavicatEncrypt import *

try:
    #########################################################Show MySQL
    print('-' * 16, 'MySQL Servers', '-' * 16, '\r\n')
    Servers_Key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\PremiumSoft\\Navicat\\Servers')
    i = 0
    try:
        while(True):
            ServerName = winreg.EnumKey(Servers_Key, i)
            print('ServerName:\t', ServerName)

            Server_Key = winreg.OpenKey(Servers_Key, ServerName)
            print('Host:\t\t', winreg.QueryValueEx(Server_Key, 'Host')[0])
            print('Port:\t\t', winreg.QueryValueEx(Server_Key, 'Port')[0])
            print('Username:\t', winreg.QueryValueEx(Server_Key, 'Username')[0])
            Pwd = winreg.QueryValueEx(Server_Key, 'Pwd')[0]
            print('Password:\t', '' if len(Pwd) == 0 else Decrypt_Navicat(bytearray.fromhex(Pwd)).decode('ascii'))

            print('-' * 32)
            winreg.CloseKey(Server_Key)
            i += 1
    except WindowsError:
        pass
    winreg.CloseKey(Servers_Key)

    ##########################################################Show MariaDB
    print('\r\n' * 2)
    print('-' * 16, 'MariaDB Servers', '-' * 16, '\r\n')
    Servers_Key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\PremiumSoft\\NavicatMARIADB\\Servers')
    i = 0
    try:
        while (True):
            ServerName = winreg.EnumKey(Servers_Key, i)
            print('ServerName:\t', ServerName)

            Server_Key = winreg.OpenKey(Servers_Key, ServerName)
            print('Host:\t\t', winreg.QueryValueEx(Server_Key, 'Host')[0])
            print('Port:\t\t', winreg.QueryValueEx(Server_Key, 'Port')[0])
            print('Username:\t', winreg.QueryValueEx(Server_Key, 'Username')[0])
            Pwd = winreg.QueryValueEx(Server_Key, 'Pwd')[0]
            print('Password:\t', '' if len(Pwd) == 0 else Decrypt_Navicat(bytearray.fromhex(Pwd)).decode('ascii'))

            print('-' * 32)
            winreg.CloseKey(Server_Key)
            i += 1
    except WindowsError:
        pass
    winreg.CloseKey(Servers_Key)

    #########################################################Show MSSQL
    print('\r\n' * 2)
    print('-' * 16, 'MSSQL Servers', '-' * 16, '\r\n')
    Servers_Key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\PremiumSoft\\NavicatMSSQL\\Servers')
    i = 0
    try:
        while (True):
            ServerName = winreg.EnumKey(Servers_Key, i)
            print('ServerName:\t', ServerName)

            Server_Key = winreg.OpenKey(Servers_Key, ServerName)
            print('Host:\t\t', winreg.QueryValueEx(Server_Key, 'Host')[0])
            print('Port:\t\t', winreg.QueryValueEx(Server_Key, 'Port')[0])
            print('Username:\t', winreg.QueryValueEx(Server_Key, 'Username')[0])
            Pwd = winreg.QueryValueEx(Server_Key, 'Pwd')[0]
            print('Password:\t', '' if len(Pwd) == 0 else Decrypt_Navicat(bytearray.fromhex(Pwd)).decode('ascii'))

            print('-' * 32)
            winreg.CloseKey(Server_Key)
            i += 1
    except WindowsError:
        pass
    winreg.CloseKey(Servers_Key)

    #########################################################Show Oracle
    print('\r\n' * 2)
    print('-' * 16, 'Oracle Servers', '-' * 16, '\r\n')
    Servers_Key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\PremiumSoft\\NavicatOra\\Servers')
    i = 0
    try:
        while (True):
            ServerName = winreg.EnumKey(Servers_Key, i)
            print('ServerName:\t\t', ServerName)

            Server_Key = winreg.OpenKey(Servers_Key, ServerName)
            print('Host:\t\t\t', winreg.QueryValueEx(Server_Key, 'Host')[0])
            print('Port:\t\t\t', winreg.QueryValueEx(Server_Key, 'Port')[0])
            print('InitialDatabase:\t', winreg.QueryValueEx(Server_Key, 'InitialDatabase')[0])
            print('Username:\t\t', winreg.QueryValueEx(Server_Key, 'Username')[0])
            Pwd = winreg.QueryValueEx(Server_Key, 'Pwd')[0]
            print('Password:\t\t', '' if len(Pwd) == 0 else Decrypt_Navicat(bytearray.fromhex(Pwd)).decode('ascii'))

            print('-' * 32)
            winreg.CloseKey(Server_Key)
            i += 1
    except WindowsError:
        pass
    winreg.CloseKey(Servers_Key)

    #########################################################Show PostgreSQL
    print('\r\n' * 2)
    print('-' * 16, 'PostgreSQL Servers', '-' * 16, '\r\n')
    Servers_Key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\PremiumSoft\\NavicatPG\\Servers')
    i = 0
    try:
        while (True):
            ServerName = winreg.EnumKey(Servers_Key, i)
            print('ServerName:\t\t', ServerName)

            Server_Key = winreg.OpenKey(Servers_Key, ServerName)
            print('Host:\t\t\t', winreg.QueryValueEx(Server_Key, 'Host')[0])
            print('Port:\t\t\t', winreg.QueryValueEx(Server_Key, 'Port')[0])
            print('InitialDatabase:\t', winreg.QueryValueEx(Server_Key, 'InitialDatabase')[0])
            print('Username:\t\t', winreg.QueryValueEx(Server_Key, 'Username')[0])
            Pwd = winreg.QueryValueEx(Server_Key, 'Pwd')[0]
            print('Password:\t\t', '' if len(Pwd) == 0 else Decrypt_Navicat(bytearray.fromhex(Pwd)).decode('ascii'))

            print('-' * 32)
            winreg.CloseKey(Server_Key)
            i += 1
    except WindowsError:
        pass
    winreg.CloseKey(Servers_Key)
except WindowsError:
    exit(WindowsError.errno)
