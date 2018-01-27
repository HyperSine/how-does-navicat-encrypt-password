import sys
from NavicatCrypto import *

def Help():
    print('Usage:')
    print('    NavicatCryptoHelper.py <-e|-d> [-ncx] <password_string|hex_string>')

if __name__ == '__main__':
    NavicatCipher = Navicat12Crypto()

    if len(sys.argv) == 3:
        if sys.argv[1] == '-e':
            print(NavicatCipher.EncryptString(sys.argv[2]))
        elif sys.argv[1] == '-d':
            print(NavicatCipher.DecryptString(sys.argv[2]))
        else:
            Help()
    elif len(sys.argv) == 4:
        if sys.argv[1] == '-e' and sys.argv[2] == '-ncx':
            print(NavicatCipher.EncryptStringForNCX(sys.argv[3]))
        elif sys.argv[1] == '-d' and sys.argv[2] == '-ncx':
            print(NavicatCipher.DecryptStringForNCX(sys.argv[3]))
        else:
            Help()
    else:
        Help()

    print()
