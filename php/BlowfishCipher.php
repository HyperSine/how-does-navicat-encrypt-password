<?php


namespace Security;

require_once('BlowfishHelper.php');
require_once('BlowfishCipherConstants.php');

class BlowfishCipher
{
    private array $ZeroSalt;
    private array $Magic;
    private array $P;
    private array $S;

    public function __construct()
    {
        $this->ZeroSalt = array_fill(0, BlowfishCipherConstants::$N, 0x0);
        $this->P = array_slice(BlowfishCipherConstants::$P, 0, count(BlowfishCipherConstants::$P), true);
        $this->S = array_slice(BlowfishCipherConstants::$S, 0, count(BlowfishCipherConstants::$S), true);
    }

    public function ExpandKey(array $key, array $salt = [])
    {
        if (empty($salt)) $salt = $this->ZeroSalt;

        $j = 0;
        for ($i = 0; $i < count($this->P); $i++) {
            $data = 0x00000000;

            for ($k = 0; $k < 4; $k++) {
                $data = ($data << 8) | $key[$j];

                if (++$j >= count($key)) {
                    $j = 0;
                }
            }
            $this->P[$i] = $this->P[$i] ^ $data;
        }

        $saltL0 = BlowfishHelper::BytesToUInt32($salt, 0);
        $saltR0 = BlowfishHelper::BytesToUInt32($salt, 4);
        $saltL1 = BlowfishHelper::BytesToUInt32($salt, 8);
        $saltR1 = BlowfishHelper::BytesToUInt32($salt, 12);

        $dataL = 0x00000000;
        $dataR = 0x00000000;

        for ($i = 0; $i < count($this->P); $i += 4) {
            $dataL ^= $saltL0;
            $dataR ^= $saltR0;

            $this->_encipher($dataL, $dataR);

            $this->P[$i + 0] = $dataL;
            $this->P[$i + 1] = $dataR;

            if ($i + 2 == count($this->P)) {
                break;
            }

            $dataL ^= $saltL1;
            $dataR ^= $saltR1;
            $this->_encipher($dataL, $dataR);

            $this->P[$i + 2] = $dataL;
            $this->P[$i + 3] = $dataR;
        }

        for ($i = 0; $i < count($this->S); $i++) {
            for ($j = 0; $j < count($this->S[$i]); $j += 4) {
                $dataL ^= $saltL1;
                $dataR ^= $saltR1;
                $this->_encipher($dataL, $dataR);
                $this->S[$i][$j + 0] = $dataL;
                $this->S[$i][$j + 1] = $dataR;

                $dataL ^= $saltL0;
                $dataR ^= $saltR0;
                $this->_encipher($dataL, $dataR);
                $this->S[$i][$j + 2] = $dataL;
                $this->S[$i][$j + 3] = $dataR;
            }
        }
    }

    public function Encipher(array &$inputBuffer, int $inputOffset, array &$outputBuffer, int $outputOffset)
    {
        $xl = BlowfishHelper::BytesToUInt32($inputBuffer, $inputOffset + 0);
        $xr = BlowfishHelper::BytesToUInt32($inputBuffer, $inputOffset + 4);
        $this->_encipher($xl, $xr);
        BlowfishHelper::UInt32ToBytes($xl, $outputBuffer, $outputOffset + 0);
        BlowfishHelper::UInt32ToBytes($xr, $outputBuffer, $outputOffset + 4);
    }

    /**
     * BlowfishCipher enciphering algorithm
     * @access private
     * @param $xL
     * @param $xR
     */
    private function _encipher(&$xL, &$xR)
    {
        $_xL = $xL;
        $_xR = $xR;

        for ($i = 0; $i < BlowfishCipherConstants::$N; $i++) {
            $_xL ^= $this->P[$i];
            $_xR = $this->_F($_xL) ^ $_xR;
            list($_xL, $_xR) = array($_xR, $_xL);
        }
        list($_xL, $_xR) = array($_xR, $_xL);

        $_xR ^= $this->P[BlowfishCipherConstants::$N];
        $_xL ^= $this->P[BlowfishCipherConstants::$N + 1];

        $xL = $_xL;
        $xR = $_xR;
    }

    public function Decipher(array &$inputBuffer, int $inputOffset, array &$outputBuffer, int $outputOffset)
    {
        $xl = BlowfishHelper::BytesToUInt32($inputBuffer, $inputOffset + 0);
        $xr = BlowfishHelper::BytesToUInt32($inputBuffer, $inputOffset + 4);
        $this->_decipher($xl, $xr);
        BlowfishHelper::UInt32ToBytes($xl, $outputBuffer, $outputOffset + 0);
        BlowfishHelper::UInt32ToBytes($xr, $outputBuffer, $outputOffset + 4);
    }

    /**
     * BlowfishCipher deciphering algorithm
     * @access private
     * @param $xL
     * @param $xR
     */
    private function _decipher(&$xL, &$xR)
    {
        $_xL = $xL;
        $_xR = $xR;

        for ($i = BlowfishCipherConstants::$N + 1; $i > 1; $i--) {
            $_xL ^= $this->P[$i];
            $_xR = $this->_F($_xL) ^ $_xR;
            list($_xL, $_xR) = array($_xR, $_xL);
        }

        list($_xL, $_xR) = array($_xR, $_xL);
        $_xR ^= $this->P[1];
        $_xL ^= $this->P[0];

        $xL = $_xL;
        $xR = $_xR;
    }

    /**
     * BlowfishCipher non-reversible F function
     * @access private
     * @param $x
     * @return int
     */
    private function _F($x): int
    {
        $d = $x & 0x00FF;
        $x >>= 8;
        $c = $x & 0x00FF;
        $x >>= 8;
        $b = $x & 0x00FF;
        $x >>= 8;
        $a = $x & 0x00FF;

        $y = $this->S[0][$a] + $this->S[1][$b];
        BlowfishHelper::UInt($y);
        $y ^= $this->S[2][$c];
        BlowfishHelper::UInt($y);
        $y += $this->S[3][$d];
        BlowfishHelper::UInt($y);

        return $y;
    }
}