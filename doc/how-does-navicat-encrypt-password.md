# How does Navicat encrypt password?

Navicat use blowfish algorithm to encrypt password string. The following is what Navicat did:

## 1. Generate Key.

Navicat use SHA-1 algorithm to generate a 160-bits-long key.

The SHA-1 digest of an ASCII string `"3DC5CA39"`, which is 8 bytes long, is the key used in blowfish cipher.

The exact value is:

```cpp
unsigned char Key[20] = {
    0x42, 0xCE, 0xB2, 0x71, 0xA5, 0xE4, 0x58, 0xB7,
    0x4A, 0xEA, 0x93, 0x94, 0x79, 0x22, 0x35, 0x43,
    0x91, 0x87, 0x33, 0x40
};
```

## 2. Initialize Initial Vector(IV).

We know that blowfish algorithm could only encrypt an **8-bytes-long** block every time.

At the beginning, Navicat fills an **8-bytes-long** block with `0xFF`, then uses blowfish algorithm encrypt the block by the key mentioned above. After that the 8-bytes-long block is Initial Vector(IV).

The exact value of IV is:

```cpp
unsigned char IV[8] = {
    0xD9, 0xC7, 0xC3, 0xC8, 0x87, 0x0D, 0x64, 0xBD
};
```

## 3. Encrypt Password String.

__NOTICE: Here, all password strings are ASCII string, and we **DO NOT** consider the "NULL" terminator.__

Navicat uses a pipeline to encrypt password string. The pipeline is showed below:

<div align="center">
    <img src = "EncryptionPipeline.png">
</div>

__NOTICE: Every plaintext block is an 8-bytes-long block. Only when the last plaintext block is not 8-bytes-long, will the last step showed in the picture above be executed. Otherwise, the last step is just like the middle two steps.__

## 4. Store The Encrypted Password.

The encrypted password stored in Windows Registry is the join of hex strings of every cipher blocks.

## 5. Addition: Password Encryption In NCX file.

### 5.1. What is NCX file?

NCX file is Navicat Connection eXport file. When you export your connection configurations for backup, Navicat will generate it. If you choose to export passwords, the encrypted passwords will be stored in NCX file you get.

### 5.2. Encryption Algorithm.

Navicat 11 and Navicat 12 use different algorithm to encrypt password.

* In Navicat 11, the encryption algorithm used is exactly the same with what I said before.

* In Navicat 12, the encryption algorithm is __AES128/CBC/PKCS7Padding__, where key is:

  ```cpp
  unsigned char AesKey[16] = {
      'l', 'i', 'b', 'c', 'c', 'k', 'e', 'y',
      'l', 'i', 'b', 'c', 'c', 'k', 'e', 'y'
  };
  ```

  And initial vector is:

  ```cpp
  unsigned char AesIV[16] = {
      'l', 'i', 'b', 'c', 'c', 'i', 'v', ' ',
      'l', 'i', 'b', 'c', 'c', 'i', 'v', ' '
  };
  ```

