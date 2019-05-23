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
    |MongoDB      |HKEY_CURRENT_USER\\Software\\PremiumSoft\\NavicatMONGODB\\Servers\\`<your connection name>`|
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

## 2. How to use the sample code in python3 folder?

* Please make sure that you have `Python3`.

* Please make sure that you have `pycryptodome` module if you want to use `NavicatCipher.py` and `NcxReader.py`.

  You can install `pycryptodome` module by command:

  ```console
  $ pip install pycryptodome
  ```

* Please make sure that you have `pypiwin32` module if you want to use `ShowNavicat.py`.

  You can install `pypiwin32` module by command:

  ```console
  $ pip install pypiwin32
  ```

1. __NavicatCipher.py__

   ```
   Usage:
       NavicatCrypto.py <enc|dec> [-ncx] <plaintext|ciphertext>

       <enc|dec>                "enc" for encryption, "dec" for decryption.
                                This parameter must be specified.

       [-ncx]                   Indicate that plaintext/ciphertext is
                                prepared for/exported from NCX file.
                                This parameter is optional.

       <plaintext|ciphertext>   Plaintext string or ciphertext string.
                                NOTICE: Ciphertext string must be a hex string.
                                This parameter must be specified.
   ```

   __Example:__

   ```console
   $ ./NavicatCipher.py enc "This is a test"
   0EA71F51DD37BFB60CCBA219BE3A

   $ ./NavicatCipher.py dec 0EA71F51DD37BFB60CCBA219BE3A
   This is a test

   $ ./NavicatCipher.py enc -ncx "This is a test"
   B75D320B6211468D63EB3B67C9E85933

   $ ./NavicatCipher.py dec -ncx B75D320B6211468D63EB3B67C9E85933
   This is a test

   $ python3
   Python 3.6.7 (default, Oct 22 2018, 11:32:17)
   [GCC 8.2.0] on linux
   Type "help", "copyright", "credits" or "license" for more information.
   >>> from NavicatCipher import *
   >>> cipher = Navicat12Crypto()
   >>> cipher.EncryptString('This is a test')
   '0EA71F51DD37BFB60CCBA219BE3A'

   >>> cipher.DecryptString('0EA71F51DD37BFB60CCBA219BE3A')
   'This is a test'

   >>> cipher.EncryptStringForNCX('This is a test')
   'B75D320B6211468D63EB3B67C9E85933'

   >>> cipher.DecryptStringForNCX('B75D320B6211468D63EB3B67C9E85933')
   'This is a test'
   ```

2. __NcxReader.py__

   Show DB servers' information inside `*.ncx` file.

   ```
   Usage:
       NcxReader.py <Path to ncx file>
   ```

   __Example:__

   ```console
   $ ./NcxReader ~/connectioms.ncx
   -----------------xxxxxxxxxxxx--------------------
   Connection Type  = MYSQL
   Host             = localhost
   Port             = 3306
   UserName         = root
   Password         = 12345678

   ------------------yyyyyyyyyy---------------------
   Connection Type  = MYSQL
   Host             = example.com
   Port             = 3306
   UserName         = server
   Password         = 0000000000

   ...
   ...
   ...
   ```

3. __ShowNavicat.py__

   Just run it in Windows. It will list all Navicat configurations inside Windows Registry.

   __Example:__

   ```console
   >ShowNavicat.py
   +--------------------------------------------------+
   |                   MySQL Server                   |
   +--------------------------------------------------+

   Host:              example.com
   Port:              3306
   Username:          server
   Password:          0000000000

   ...
   ...

   +--------------------------------------------------+
   |                  MariaDB Server                  |
   +--------------------------------------------------+

   ...
   ...

   +--------------------------------------------------+
   |                  MongoDB Server                  |
   +--------------------------------------------------+

   ...
   ...

   ...
   ...
   ```