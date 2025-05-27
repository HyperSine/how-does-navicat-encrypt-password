#!/usr/bin/env python3
import platform
import sys, winreg
import utils.navicat_route_finder as nrf
from utils.navicat_11_crypto import Navicat11Crypto

if platform.system().lower() != 'windows':
    print('Please run this script in Windows.')
    exit(-1)

HIVE_VALUE = winreg.HKEY_CURRENT_USER
KEY_PATH = 'Software\\PremiumSoft\\NavicatPremium'

NavicatCipher = Navicat11Crypto()
projects_found = nrf.find_projects_recursive(HIVE_VALUE, KEY_PATH)

NewServersTypes = {
    project['path'].split('\\')[9]: '\\'.join(project['path'].split('\\')[:-2])
    for project in projects_found
}

ServersTypes = {
    'MySQL Server' : 'Software\\PremiumSoft\\Navicat\\Servers',
    'MariaDB Server' : 'Software\\PremiumSoft\\NavicatMARIADB\\Servers',
    'MongoDB Server' : 'Software\\PremiumSoft\\NavicatMONGODB\\Servers',
    'MSSQL Server' : 'Software\\PremiumSoft\\NavicatMSSQL\\Servers',
    'OracleSQL Server' : 'Software\\PremiumSoft\\NavicatOra\\Servers',
    'PostgreSQL Server' : 'Software\\PremiumSoft\\NavicatPG\\Servers',
}

ServersTypes.update(NewServersTypes)

for ServersTypeName, ServersRegistryPath in ServersTypes.items():
    print('+--------------------------------------------------+')
    print(f'|{ServersTypeName.center(50)}|')
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
                ServerHost = nrf.find_value_if_exists(ServerRegistryKey, 'Host')
                ServerPort = nrf.find_value_if_exists(ServerRegistryKey, 'Port')
                ServerInitialDb = nrf.find_value_if_exists(ServerRegistryKey, 'InitialDatabase')
                ServerUsername = nrf.find_value_if_exists(ServerRegistryKey, 'Username')
                ServerPassword = nrf.find_value_if_exists(ServerRegistryKey, 'Pwd')

                if ServerPassword is not None and len(ServerPassword) != 0:
                    ServerPassword = NavicatCipher.DecryptString(ServerPassword)

                ServerUseSsh = nrf.find_value_if_exists(ServerRegistryKey, 'UseSSH')
                ServerSshHost = nrf.find_value_if_exists(ServerRegistryKey, 'SSH_Host')
                ServerSshPort = nrf.find_value_if_exists(ServerRegistryKey, 'SSH_Port')
                ServerSshUsername = nrf.find_value_if_exists(ServerRegistryKey, 'SSH_Username')
                ServerSshPassword = nrf.find_value_if_exists(ServerRegistryKey, 'SSH_Password')
                if ServerSshPassword is not None and len(ServerSshPassword) != 0:
                    ServerSshPassword = NavicatCipher.DecryptString(ServerSshPassword)

                print(ServerName.center(50, '*'))
                print(f'{"Host:":<18} {ServerHost}')
                print(f'{"Port:":<18} {ServerPort}')
                if ServerInitialDb is not None:
                    print(f'{"InitialDb:":<18} {ServerInitialDb}')
                print(f'{"Username:":<18} {ServerUsername}')
                print(f'{"Password:":<18} {ServerPassword}')

                if ServerUseSsh:
                    print(f'{"SSH Host:":<18} {ServerSshHost}')
                    print(f'{"SSH Port:":<18} {ServerSshPort}')
                    print(f'{"SSH Username:":<18} {ServerSshUsername}')
                    print(f'{"SSH Password:":<18} {ServerSshPassword}')

            except (OSError, PermissionError, FileNotFoundError) as e:
                print('[-] Failed to get info about server "%s". Server info may be corrupted.' % ServerName, file = sys.stderr)
                print('[-] Error: %s' % e, file = sys.stderr)

            winreg.CloseKey(ServerRegistryKey)
            i += 1
    except OSError:
        if i == 0:
            print('No servers is found.')
            print('')
        continue
