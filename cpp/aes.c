#include "aes.h"

#if defined(_MSC_VER)
#include <intrin.h>
#elif defined(__GNUC__)
#include <x86intrin.h>
#endif

extern const uint32_t accel_AES_rcon[11];

extern const uint8_t accel_AES_SBox[256];
extern const uint8_t accel_AES_InverseSBox[256];

extern const uint8_t accel_AES_GF2p8_Mul_0x02[256];
extern const uint8_t accel_AES_GF2p8_Mul_0x03[256];
extern const uint8_t accel_AES_GF2p8_Mul_0x09[256];
extern const uint8_t accel_AES_GF2p8_Mul_0x0B[256];
extern const uint8_t accel_AES_GF2p8_Mul_0x0D[256];
extern const uint8_t accel_AES_GF2p8_Mul_0x0E[256];

#define Swap(X, Y, Temp)    \
    Temp = X;               \
    X = Y;                  \
    Y = Temp;

void accel_AES128_encrypt(uint8_t srcBytes[AES_BLOCK_SIZE], const ACCEL_AES_KEY* srcKey) {
    ((uint64_t*)srcBytes)[0] ^= srcKey->qword[0];
    ((uint64_t*)srcBytes)[1] ^= srcKey->qword[1];

    uint8_t ShiftTemp = 0;
    for (int i = 1; i < 10; ++i) {

        for (int j = 0; j < 16; ++j)
            srcBytes[j] = accel_AES_SBox[srcBytes[j]];

        //Shift rows starts;
        //Shift the second row;
        Swap(srcBytes[1], srcBytes[5], ShiftTemp)
        Swap(srcBytes[5], srcBytes[9], ShiftTemp)
        Swap(srcBytes[9], srcBytes[13], ShiftTemp)
        //Shift the third row;
        Swap(srcBytes[2], srcBytes[10], ShiftTemp)
        Swap(srcBytes[6], srcBytes[14], ShiftTemp)
        //Shift the fourth row;
        Swap(srcBytes[3], srcBytes[15], ShiftTemp)
        Swap(srcBytes[15], srcBytes[11], ShiftTemp)
        Swap(srcBytes[11], srcBytes[7], ShiftTemp)
        //Shift rows ends;


        for (int j = 0; j < 16; j += 4) {
            uint8_t temp[4];
            *(uint32_t*)temp = ((uint32_t*)srcBytes)[j / 4];

            srcBytes[j] = (uint8_t)(accel_AES_GF2p8_Mul_0x02[temp[0]] ^ accel_AES_GF2p8_Mul_0x03[temp[1]] ^ temp[2] ^ temp[3]);
            srcBytes[j + 1] = (uint8_t)(temp[0] ^ accel_AES_GF2p8_Mul_0x02[temp[1]] ^ accel_AES_GF2p8_Mul_0x03[temp[2]] ^ temp[3]);
            srcBytes[j + 2] = (uint8_t)(temp[0] ^ temp[1] ^ accel_AES_GF2p8_Mul_0x02[temp[2]] ^ accel_AES_GF2p8_Mul_0x03[temp[3]]);
            srcBytes[j + 3] = (uint8_t)(accel_AES_GF2p8_Mul_0x03[temp[0]] ^ temp[1] ^ temp[2] ^ accel_AES_GF2p8_Mul_0x02[temp[3]]);
        }

        ((uint64_t*)(srcBytes))[0] ^= srcKey->qword[i * 2];
        ((uint64_t*)(srcBytes))[1] ^= srcKey->qword[i * 2 + 1];
    }

    for (int j = 0; j < 16; ++j)
        srcBytes[j] = accel_AES_SBox[srcBytes[j]];

    //Shift rows starts;
    //Shift the second row;
    Swap(srcBytes[1], srcBytes[5], ShiftTemp)
    Swap(srcBytes[5], srcBytes[9], ShiftTemp)
    Swap(srcBytes[9], srcBytes[13], ShiftTemp)
    //Shift the third row;
    Swap(srcBytes[2], srcBytes[10], ShiftTemp)
    Swap(srcBytes[6], srcBytes[14], ShiftTemp)
    //Shift the fourth row;
    Swap(srcBytes[3], srcBytes[15], ShiftTemp)
    Swap(srcBytes[15], srcBytes[11], ShiftTemp)
    Swap(srcBytes[11], srcBytes[7], ShiftTemp)
    //Shift rows ends;

    ((uint64_t*)srcBytes)[0] ^= srcKey->qword[20];
    ((uint64_t*)srcBytes)[1] ^= srcKey->qword[21];
}

void accel_AES128_decrypt(uint8_t srcBytes[AES_BLOCK_SIZE], const ACCEL_AES_KEY* srcKey) {
    ((uint64_t*)srcBytes)[0] ^= srcKey->qword[20];
    ((uint64_t*)srcBytes)[1] ^= srcKey->qword[21];

    uint8_t ShiftTemp = 0;

    for (int i = 9; i > 0; --i) {
        //Inverse Shift rows starts;
        //Inverse shift the second row;
        Swap(srcBytes[13], srcBytes[9], ShiftTemp)
        Swap(srcBytes[9], srcBytes[5], ShiftTemp)
        Swap(srcBytes[5], srcBytes[1], ShiftTemp)
        //Inverse shift the third row;
        Swap(srcBytes[14], srcBytes[6], ShiftTemp)
        Swap(srcBytes[10], srcBytes[2], ShiftTemp)
        //Inverse shift the fourth row;
        Swap(srcBytes[3], srcBytes[7], ShiftTemp)
        Swap(srcBytes[7], srcBytes[11], ShiftTemp)
        Swap(srcBytes[11], srcBytes[15], ShiftTemp)

        for (int j = 0; j < 16; ++j)
            srcBytes[j] = accel_AES_InverseSBox[srcBytes[j]];

        ((uint64_t*)srcBytes)[0] ^= srcKey->qword[i * 2];
        ((uint64_t*)srcBytes)[1] ^= srcKey->qword[i * 2 + 1];

        for (int j = 0; j < 16; j += 4) {
            uint8_t temp[4];
            *(uint32_t*)temp = ((uint32_t*)srcBytes)[j / 4];
            srcBytes[j + 0] = (uint8_t)(accel_AES_GF2p8_Mul_0x0E[temp[0]] ^
                                        accel_AES_GF2p8_Mul_0x0B[temp[1]] ^
                                        accel_AES_GF2p8_Mul_0x0D[temp[2]] ^
                                        accel_AES_GF2p8_Mul_0x09[temp[3]]);

            srcBytes[j + 1] = (uint8_t)(accel_AES_GF2p8_Mul_0x09[temp[0]] ^ 
                                        accel_AES_GF2p8_Mul_0x0E[temp[1]] ^ 
                                        accel_AES_GF2p8_Mul_0x0B[temp[2]] ^ 
                                        accel_AES_GF2p8_Mul_0x0D[temp[3]]);

            srcBytes[j + 2] = (uint8_t)(accel_AES_GF2p8_Mul_0x0D[temp[0]] ^ 
                                        accel_AES_GF2p8_Mul_0x09[temp[1]] ^ 
                                        accel_AES_GF2p8_Mul_0x0E[temp[2]] ^ 
                                        accel_AES_GF2p8_Mul_0x0B[temp[3]]);

            srcBytes[j + 3] = (uint8_t)(accel_AES_GF2p8_Mul_0x0B[temp[0]] ^ 
                                        accel_AES_GF2p8_Mul_0x0D[temp[1]] ^ 
                                        accel_AES_GF2p8_Mul_0x09[temp[2]] ^ 
                                        accel_AES_GF2p8_Mul_0x0E[temp[3]]);
        }
    }

    //Inverse Shift rows starts;
    //Inverse shift the second row;
    Swap(srcBytes[13], srcBytes[9], ShiftTemp)
    Swap(srcBytes[9], srcBytes[5], ShiftTemp)
    Swap(srcBytes[5], srcBytes[1], ShiftTemp)
    //Inverse shift the third row;
    Swap(srcBytes[14], srcBytes[6], ShiftTemp)
    Swap(srcBytes[10], srcBytes[2], ShiftTemp)
    //Inverse shift the fourth row;
    Swap(srcBytes[3], srcBytes[7], ShiftTemp)
    Swap(srcBytes[7], srcBytes[11], ShiftTemp)
    Swap(srcBytes[11], srcBytes[15], ShiftTemp)

    for (int j = 0; j < 16; ++j)
        srcBytes[j] = accel_AES_InverseSBox[srcBytes[j]];

    ((uint64_t*)srcBytes)[0] ^= srcKey->qword[0];
    ((uint64_t*)srcBytes)[1] ^= srcKey->qword[1];
}

void accel_AES128_set_key(const uint8_t srcUserKey[AES128_USERKEY_LENGTH], ACCEL_AES_KEY* dstKey) {
    dstKey->qword[0] = ((const uint64_t*)srcUserKey)[0];
    dstKey->qword[1] = ((const uint64_t*)srcUserKey)[1];

    for (int i = 4; i < 44; ++i) {
        uint32_t temp = dstKey->dword[i - 1];
        if (i % 4 == 0) {
            temp = _rotr(temp, 8);
            ((uint8_t*)&temp)[0] = accel_AES_SBox[((uint8_t*)&temp)[0]];
            ((uint8_t*)&temp)[1] = accel_AES_SBox[((uint8_t*)&temp)[1]];
            ((uint8_t*)&temp)[2] = accel_AES_SBox[((uint8_t*)&temp)[2]];
            ((uint8_t*)&temp)[3] = accel_AES_SBox[((uint8_t*)&temp)[3]];
            temp ^= accel_AES_rcon[i / 4];
        }
        dstKey->dword[i] = dstKey->dword[i - 4] ^ temp;
    }
}
