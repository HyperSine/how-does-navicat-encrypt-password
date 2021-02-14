<?php
/**
 * Created by PhpStorm.
 * User: Maurice
 * Date: 6-6-2018
 * Time: 22:17
 */

use Security\BlowfishCipher;
use Security\BlowfishHelper;

require_once('BlowfishCipher.php');
/**
 * Class NavicatEncrypt
 */
class NavicatEncrypt
{
    /**
     * @var string
     */
    private string $navicatCode = "3DC5CA39";
    /**
     * @var array|int[]
     */
    private array $key = [0x42, 0xCE, 0xB2, 0x71, 0xA5, 0xE4, 0x58, 0xB7, 0x4A, 0xEA, 0x93, 0x94, 0x79, 0x22, 0x35, 0x43, 0x91, 0x87, 0x33, 0x40];
    /**
     * @var array|int[]
     */
    private array $iv = [0xD9, 0xC7, 0xC3, 0xC8, 0x87, 0x0D, 0x64, 0xBD];

    /**
     * @param string $input
     * @return string
     */
    public function Encrypt(string $input): string
    {
        $bf = new BlowfishCipher();
        $bf->ExpandKey($this->key, []);

        $inData = unpack('C*', $input);

        $CV = array_slice($this->iv, 0, count($this->iv), true);
        $ret = array_fill(0, count($inData) - 1, 0x0);

        $rounded = intdiv(count($inData), 8);
        $left = count($inData);

        if ($rounded > 0) {
            $left = count($inData) - ($rounded * 8);
        }

        for ($i = 0; $i < $rounded; $i++) {
            $tmp = array_slice($inData, $i * 8, 8);
            $this->XorBytes($tmp, $CV);

            $bf->Encipher($tmp, 0, $tmp, 0);

            $this->XorBytes($CV, $tmp);

            for ($j = 0; $j < count($tmp); $j++) {
                $ret[($i*8)+$j] = $tmp[$j];
            }
        }

        if ($left > 0) {
            $bf->Encipher($CV, 0, $CV, 0);

            $tmp = array_slice($inData, $rounded * 8, $left);
            $this->XorBytes($tmp, $CV, $left);

            for ($j = 0; $j < count($tmp); $j++) {
                $ret[($rounded * 8) + $j] = $tmp[$j];
            }
        }

        return BlowfishHelper::byteArray2HexString($ret);
    }

    public function Decrypt(string $input):string
    {
        $bf = new BlowfishCipher();
        $bf->ExpandKey($this->key, []);

        $inData = BlowfishHelper::hexString2ByteArray($input);

        $CV = array_slice($this->iv, 0, count($this->iv), true);
        $ret = array_fill(0, count($inData) - 1, 0x0);

        $rounded = intdiv(count($inData), 8);
        $left = count($inData);

        if ($rounded > 0) {
            $left = count($inData) - ($rounded * 8);
        }

        for ($i = 0; $i < $rounded; $i++) {
            $tmp = array_slice($inData, $i * 8, 8);
            $bf->Decipher($tmp,0,$tmp,0);

            $this->XorBytes($tmp, $CV);

            for ($j = 0; $j < count($tmp); $j++) {
                $ret[($i*8)+$j] = $tmp[$j];
            }

            for ( $j = 0; $j < count($CV); $j++) {
                $CV[$j] = $CV[$j] ^ $inData[($i * 8) + $j];
            }
        }

        if ($left > 0) {
            $bf->Encipher($CV, 0, $CV, 0);

            $tmp = array_slice($inData, $rounded * 8, $left);
            $this->XorBytes($tmp, $CV, $left);

            for ($j = 0; $j < count($tmp); $j++) {
                $ret[($rounded * 8) + $j] = $tmp[$j];
            }
        }

        return BlowfishHelper::byteArray2String($ret);
    }

    /**
     * @param array $a
     * @param array $b
     * @param false $l
     */
    private function XorBytes(array &$a, array &$b, $l = false)
    {
        if ($l === false) {
            $l = count($a);
        }
        for ($i = 0; $i < $l; $i++) {
            $a[$i] = $a[$i] ^ $b[$i];
        }
    }


}