# How Does Navicat Encrypt Password?

## 1. What is Navicat?
  * Navicat is a series of graphical database management and development software produced by PremiumSoft CyberTech Ltd. for MySQL, MariaDB, Oracle, SQLite, PostgreSQL and Microsoft SQL Server.

  * It has an Explorer-like graphical user interface and supports multiple database connections for local and remote databases. Its design is made to meet the needs of a variety of audiences, from database administrators and programmers to various businesses/companies that serve clients and share information with partners.

## 2. What does indicate that Navicat encrypts password?
  * If you use Navicat to manage one of your databases, the first thing you should do is to create a connection to the database. So that means you should fill textboxes on the window showed below with the database's information like `host name`, `User name`, `Password` and so on.

    <div align="center">
      <img src = "NavicatSetUpConnection.gif">
    </div>

  * If you check "Save Password", after you click "Ok" button, Navicat will encrypt the password and then save the connection configuration, containing encrypted password, in **Windows Registry**. The exact path is showed below:

    |Database Type|Path                                                                                       |
    |-------------|-------------------------------------------------------------------------------------------|
    |MySQL        |HKEY_CURRENT_USER\\Software\\PremiumSoft\\Navicat\\Servers\\`<your connection name>`       |
    |MariaDB      |HKEY_CURRENT_USER\\Software\\PremiumSoft\\NavicatMARIADB\\Servers\\`<your connection name>`|
    |Microsoft SQL|HKEY_CURRENT_USER\\Software\\PremiumSoft\\NavicatMSSQL\\Servers\\`<your connection name>`  |
    |Oracle       |HKEY_CURRENT_USER\\Software\\PremiumSoft\\NavicatOra\\Servers\\`<your connection name>`    |
    |PostgreSQL   |HKEY_CURRENT_USER\\Software\\PremiumSoft\\NavicatPG\\Servers\\`<your connection name>`     |
    |SQLite       |HKEY_CURRENT_USER\\Software\\PremiumSoft\\NavicatSQLite\\Servers\\`<your connection name>` |

  * Here blow is an example:

    <div align="center">
      <img src = "NavicatInRegistry.PNG">
    </div>

## 3. How does Navicat encrypt password?
Navicat use blowfish algorithm to encrypt password string. Here below is what Navicat did:

### 1. Generate Key.  
  * Navicat use SHA-1 algorithm to generate a 160-bits' key.

  * The SHA-1 digest of an ASCII string---**"3DC5CA39"**, 8 bytes long---is the key used in blowfish cipher.

  * The exact value is:

    ~~~cpp
    unsigned char Key[20] = {
        0x42, 0xCE, 0xB2, 0x71, 0xA5, 0xE4, 0x58, 0xB7,
        0x4A, 0xEA, 0x93, 0x94, 0x79, 0x22, 0x35, 0x43,
        0x91, 0x87, 0x33, 0x40
    };
    ~~~

### 2. Initialize Initial Vector(IV)
  * We know that blowfish algorithm could only encrypt an **8-bytes-long** block every time.

  * At the beginning, Navicat fills an **8-bytes-long** block with **0xFF**, then uses blowfish algorithm encrypt the block by the key mentioned above. After that the 8-bytes-long block is Initial Vector(IV).

  * The exact value of IV is:

    ~~~cpp
    unsigned char IV[8] = {
        0xD9, 0xC7, 0xC3, 0xC8, 0x87, 0x0D, 0x64, 0xBD
    };
    ~~~

### 3. Encrypt Password String.
  * NOTICE: Here, the password string is an ASCII string, and we **DO NOT** consider the "NULL" terminator.

  * Navicat use a pipeline to encrypt password string. The pipeline is showed below:

    <div align="center">
      <img src = "EncryptionPipeline.png">
    </div>

  * NOTICE: Every plaintext block is an 8-bytes-long block. Only when the last plaintext block is not 8-bytes-long, will the last step showed in the picture above be executed. Otherwise, the last step is just like the middle two steps.

### 4. Store The Encrypted Password.
  * The encrypted password stored in Windows Registry is the join of hex strings of every cipher blocks.

### 5. Addition: Password Encryption In NCX file.
#### 1. What is NCX file?
  * NCX file is Navicat Connection eXport file. When you export your connections' configuration for backup, Navicat will generate it. If you choose to export passwords, the encrypted passwords will be stored in NCX file you get.

#### 2. Encryption Algorithm.
  * Navicat 11 and Navicat 12 use different algorithm to encrypt password.

  * In Navicat 11, the encryption algorithm used is exactly the same with what I said before.

  * In Navicat 12, the encryption algorithm is __AES128/CBC/PKCS7Padding__, where the key is:

    ```cpp
    unsigned char AES_Key[16] = {
        'l', 'i', 'b', 'c', 'c', 'k', 'e', 'y',
        'l', 'i', 'b', 'c', 'c', 'k', 'e', 'y'
    };
    ```

    and initial vector is:

    ```cpp
    unsigned char AES_IV[16] = {
        'l', 'i', 'b', 'c', 'c', 'i', 'v', ' ',
        'l', 'i', 'b', 'c', 'c', 'i', 'v', ' '
    };
    ```

## 2. How to use the sample code.
  * Please make sure that you have `Python3`.

  * Please make sure that you have `blowfish`, `pycryptodome` module if you want to use `NavicatCrypto.py` and `NavicatCryptoHelper.py`. You can install `blowfish` and `pycryptodome` module by command:

    ```cmd
    pip install blowfish
    ```

  * Please make sure that you have 'pypiwin32' module if you want to use `ShowNavicat.py`. You can install 'pypiwin32' by command:

    ```cmd
    pip install pypiwin32
    ```

  * The following is a sample:

    1. __NavicatCrypto.py__

       ~~~powershell
       PS E:\GitHub\how-does-navicat-encrypt-password\python3> python
       Python 3.6.3 (v3.6.3:2c5fed8, Oct  3 2017, 18:11:49) [MSC v.1900 64 bit (AMD64)] on win32
       Type "help", "copyright", "credits" or "license" for more information.
       >>> from NavicatCrypto import *
       >>> cipher = Navicat11Crypto()
       >>> cipher.EncryptString('This is a test')
       '0EA71F51DD37BFB60CCBA219BE3A'
       >>> cipher.DecryptString('0EA71F51DD37BFB60CCBA219BE3A')
       'This is a test'
       >>> cipher2 = Navicat12Crypto()
       >>> cipher2.EncryptStringForNCX('This is a test')
       'B75D320B6211468D63EB3B67C9E85933'
       >>> cipher2.DecryptStringForNCX('B75D320B6211468D63EB3B67C9E85933')
       'This is a test'
       >>>

       ~~~

    2. __NavicatCryptoHelper.py__

       ```powershell
       PS E:\GitHub\how-does-navicat-encrypt-password\python3> .\NavicatCryptoHelper.py -e "This is a test"
       0EA71F51DD37BFB60CCBA219BE3A

       PS E:\GitHub\how-does-navicat-encrypt-password\python3> .\NavicatCryptoHelper.py -d "0EA71F51DD37BFB60CCBA219BE3A"
       This is a test

       PS E:\GitHub\how-does-navicat-encrypt-password\python3> .\NavicatCryptoHelper.py -e -ncx "This is a test"
       B75D320B6211468D63EB3B67C9E85933

       PS E:\GitHub\how-does-navicat-encrypt-password\python3> .\NavicatCryptoHelper.py -d -ncx "B75D320B6211468D63EB3B67C9E85933"
       This is a test

       PS E:\GitHub\how-does-navicat-encrypt-password\python3>
       ```

  * You can just run `ShowNavicat.py` to get all of your database passwords that were stored by Navicat in Windows Registry.
