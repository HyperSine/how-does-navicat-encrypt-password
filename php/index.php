<?php
/**
 * Created by PhpStorm.
 * User: Maurice
 * Date: 3-7-2018
 * Time: 21:48
 */

require_once ('NavicatEncrypt.php');

echo "!!! PHP NavicatEncrypt !!!<br>";
$encrypter = new NavicatEncrypt();
echo "Plaintext: @HallOD1t1seenlangWachtwoord!<br>";
echo "Encrypted: " . $encrypter->Encrypt('@HallOD1t1seenlangWachtwoord!') . "<br>";
echo "Encrypted: 81AB926F5FC6AEEFA5E4F38634591B0A8C3DD58641DE3967A127D2<br>";
echo "Plaintext: " . $encrypter->Decrypt('81AB926F5FC6AEEFA5E4F38634591B0A8C3DD58641DE3967A127D2') . "<br>";