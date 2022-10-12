<?php

namespace Security;


class BlowfishHelper
{
    public static function BytesToUInt32(array $bytes, int $offset): int
    {
        return $bytes[$offset + 0] << 24 |
            $bytes[$offset + 1] << 16 |
            $bytes[$offset + 2] << 8 |
            $bytes[$offset + 3];
    }

    public static function UInt32ToBytes(int $value, array &$bytes, int $offset)
    {
        array_splice($bytes, $offset, 4, array_reverse(unpack("C*", pack("L", $value))));
    }

    public static function UInt(int &$int)
    {
        if ($int > 4294967296) {
            $int -= 4294967296;
        }
    }

    public static function byteArray2HexString(array $byteArray): string
    {
        $chars = array_map("chr", $byteArray);
        $bin = join($chars);
        return strtoupper(bin2hex($bin));
    }
    public static function hexString2ByteArray(string $hexString): array
    {
        $string = hex2bin($hexString);
        return array_values(unpack('C*', $string));
    }

    public static function byteArray2String(array $byteArray):string
    {
        $chars = array_map("chr", $byteArray);
        return join($chars);
    }
}