import blowfish
import hashlib

IV = None
KeyString = hashlib.sha1('3DC5CA39'.encode('ascii'))
KeyBytes = bytearray.fromhex(KeyString.hexdigest())
cipher = None

def XorBytes(a, b):
    if(type(a) is not bytearray or type(b) is not bytearray):
        raise TypeError('Either a or b is not a bytearray.')
    if(len(a) != len(b)):
        raise ValueError('The length of a is not equal to the length of b.')
    for i in range(0, len(a)):
        a[i] ^= b[i]

def XorBytesWithLength(a, b, length):
    if (type(a) is not bytearray or type(b) is not bytearray):
        raise TypeError('Either a or b is not a bytearray.')
    if (type(length) is not int):
        raise TypeError('The type of length must be int')

    if (length < 0):
        raise ValueError('length must be larger than zero or be equal to zero.')
    if (len(a) < length):
        raise ValueError('length must not be larger than the length of a.')
    if (len(b) < length):
        raise ValueError('length must not be larger than the length of b.')

    for i in range(0, length):
        a[i] ^= b[i]

def InitialCipher():
    global cipher
    cipher = blowfish.Cipher(KeyBytes)

def InitializeIV():
    global IV
    IV = bytearray.fromhex('FFFFFFFFFFFFFFFF')
    IV = bytearray(cipher.encrypt_block(IV))

def Encrypt_Navicat(inData):
    global cipher, IV

    if(type(inData) != bytearray):
        raise TypeError('The type of inData is not bytearray')

    CV = bytearray(IV)
    inDataLength = len(inData)
    Ret = bytearray(inDataLength)
    Round = inDataLength // 8

    for i in range(0, Round):
        temp = bytearray(inData[i * 8 : i * 8 + 8])
        XorBytes(temp, CV)
        temp = bytearray(cipher.encrypt_block(temp))
        XorBytes(CV, temp)
        for j in range(0, len(temp)):
            Ret[i * 8 + j] = temp[j]

    Left = inDataLength % 8
    if (Left != 0):
        CV = bytearray(cipher.encrypt_block(CV))
        temp = bytearray(inData[Round * 8 : Round * 8 + Left])
        XorBytesWithLength(temp, CV, Left)
        for j in range(0, len(temp)):
            Ret[Round * 8 + j] = temp[j]

    return Ret

def Decrypt_Navicat(inData):
    global cipher, IV

    if (type(inData) != bytearray):
        raise TypeError('The type of inData is not bytearray')

    CV = bytearray(IV)
    inDataLength = len(inData)
    Ret = bytearray(inDataLength)
    Round = inDataLength // 8

    for i in range(0, Round):
        temp = bytearray(cipher.decrypt_block(inData[i * 8: i * 8 + 8]))
        XorBytes(temp, CV)
        for j in range(0, len(temp)):
            Ret[i * 8 + j] = temp[j]
        for j in range(0, len(CV)):
            CV[j] ^= inData[i * 8 + j]

    Left = inDataLength % 8
    if (Left != 0):
        CV = bytearray(cipher.encrypt_block(CV))
        temp = bytearray(inData[Round * 8: Round * 8 + Left])
        XorBytesWithLength(temp, CV, Left)
        for j in range(0, len(temp)):
            Ret[Round * 8 + j] = temp[j]

    return Ret

if __name__ == 'NavicatEncrypt':
    InitialCipher()
    InitializeIV()