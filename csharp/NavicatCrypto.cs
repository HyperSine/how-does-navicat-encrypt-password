using System;
using System.Linq;
using System.Text;
using System.IO;
using System.Security.Cryptography;

namespace NavicatCrypto {
    class Navicat11Cipher {

        private Blowfish blowfishCipher;

        protected static byte[] StringToByteArray(string hex) {
            return Enumerable.Range(0, hex.Length)
                             .Where(x => x % 2 == 0)
                             .Select(x => Convert.ToByte(hex.Substring(x, 2), 16))
                             .ToArray();
        }

        protected static string ByteArrayToString(byte[] bytes) {
            return BitConverter.ToString(bytes).Replace("-", string.Empty);
        }

        protected static void XorBytes(byte[] a, byte[] b, int len) {
            for (int i = 0; i < len; ++i)
                a[i] ^= b[i];
        }

        public Navicat11Cipher() {
            byte[] UserKey = Encoding.UTF8.GetBytes("3DC5CA39");
            var sha1 = new SHA1CryptoServiceProvider();
            sha1.TransformFinalBlock(UserKey, 0, UserKey.Length);
            blowfishCipher = new Blowfish(sha1.Hash);
        }

        public Navicat11Cipher(string CustomUserKey) {
            byte[] UserKey = Encoding.UTF8.GetBytes(CustomUserKey);
            var sha1 = new SHA1CryptoServiceProvider();
            byte[] UserKeyHash = sha1.TransformFinalBlock(UserKey, 0, 8);
            blowfishCipher = new Blowfish(UserKeyHash);
        }

        public string EncryptString(string plaintext) {
            byte[] plaintext_bytes = Encoding.UTF8.GetBytes(plaintext);

            byte[] CV = Enumerable.Repeat<byte>(0xFF, Blowfish.BlockSize).ToArray();
            blowfishCipher.Encrypt(CV, Blowfish.Endian.Big);

            string ret = "";
            int blocks_len = plaintext_bytes.Length / Blowfish.BlockSize;
            int left_len = plaintext_bytes.Length % Blowfish.BlockSize;
            byte[] temp = new byte[Blowfish.BlockSize];
            for (int i = 0; i < blocks_len; ++i) {
                Array.Copy(plaintext_bytes, Blowfish.BlockSize * i, temp, 0, Blowfish.BlockSize);
                XorBytes(temp, CV, Blowfish.BlockSize);
                blowfishCipher.Encrypt(temp, Blowfish.Endian.Big);
                XorBytes(CV, temp, Blowfish.BlockSize);

                ret += ByteArrayToString(temp);
            }

            if (left_len != 0) {
                blowfishCipher.Encrypt(CV, Blowfish.Endian.Big);
                XorBytes(CV,
                         plaintext_bytes.Skip(blocks_len * Blowfish.BlockSize).Take(left_len).ToArray(),
                         left_len);
                ret += ByteArrayToString(CV.Take(left_len).ToArray());
            }

            return ret;
        }

        public string DecryptString(string ciphertext) {
            byte[] ciphertext_bytes = StringToByteArray(ciphertext);

            byte[] CV = Enumerable.Repeat<byte>(0xFF, Blowfish.BlockSize).ToArray();
            blowfishCipher.Encrypt(CV, Blowfish.Endian.Big);

            byte[] ret = new byte[0];
            int blocks_len = ciphertext_bytes.Length / Blowfish.BlockSize;
            int left_len = ciphertext_bytes.Length % Blowfish.BlockSize;
            byte[] temp = new byte[Blowfish.BlockSize];
            byte[] temp2 = new byte[Blowfish.BlockSize];
            for (int i = 0; i < blocks_len; ++i) {
                Array.Copy(ciphertext_bytes, Blowfish.BlockSize * i, temp, 0, Blowfish.BlockSize);
                Array.Copy(temp, temp2, Blowfish.BlockSize);
                blowfishCipher.Decrypt(temp, Blowfish.Endian.Big);
                XorBytes(temp, CV, Blowfish.BlockSize);
                ret = ret.Concat(temp).ToArray();
                XorBytes(CV, temp2, Blowfish.BlockSize);
            }

            if (left_len != 0) {
                Array.Clear(temp, 0, temp.Length);
                Array.Copy(ciphertext_bytes, Blowfish.BlockSize * blocks_len, temp, 0, left_len);
                blowfishCipher.Encrypt(CV, Blowfish.Endian.Big);
                XorBytes(temp, CV, Blowfish.BlockSize);
                ret = ret.Concat(temp.Take(left_len).ToArray()).ToArray();
            }

            return Encoding.UTF8.GetString(ret);
        }
    }

    class Navicat12Cipher : Navicat11Cipher {

        private AesCryptoServiceProvider AesServiceProvider;

        public Navicat12Cipher() : base() {
            AesServiceProvider = new AesCryptoServiceProvider();
            AesServiceProvider.KeySize = 128;
            AesServiceProvider.Mode = CipherMode.CBC;
            AesServiceProvider.Padding = PaddingMode.PKCS7;

            AesServiceProvider.Key = Encoding.UTF8.GetBytes("libcckeylibcckey");
            AesServiceProvider.IV = Encoding.UTF8.GetBytes("libcciv libcciv ");
        }

        public string EncryptStringForNCX(string plaintext) {
            ICryptoTransform AesEncryptor = AesServiceProvider.CreateEncryptor();
            MemoryStream ms = new MemoryStream();
            CryptoStream cs = new CryptoStream(ms, AesEncryptor, CryptoStreamMode.Write);
            byte[] plaintext_bytes = Encoding.UTF8.GetBytes(plaintext);
            cs.Write(plaintext_bytes, 0, plaintext_bytes.Length);
            cs.FlushFinalBlock();
            return ByteArrayToString(ms.ToArray());
        }

        public string DecryptStringForNCX(string ciphertext) {
            ICryptoTransform AesDecryptor = AesServiceProvider.CreateDecryptor();
            MemoryStream ms = new MemoryStream();
            CryptoStream cs = new CryptoStream(ms, AesDecryptor, CryptoStreamMode.Write);
            byte[] ciphertext_bytes = StringToByteArray(ciphertext);
            cs.Write(ciphertext_bytes, 0, ciphertext_bytes.Length);
            cs.FlushFinalBlock();
            return Encoding.UTF8.GetString(ms.ToArray());
        }

    }
}
