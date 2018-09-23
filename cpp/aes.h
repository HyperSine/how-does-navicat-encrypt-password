#pragma once
#include <stdint.h>
#include <stddef.h>

#if defined(__cplusplus)
extern "C" {
#endif

#define AES_BLOCK_SIZE 16
#define AES128_USERKEY_LENGTH 16

    typedef struct _ACCEL_AES_KEY {
        union {
            uint8_t byte[240];
            uint16_t word[120];
            uint32_t dword[60];
            uint64_t qword[30];
        };
    } ACCEL_AES_KEY;

    void accel_AES128_encrypt(uint8_t srcBytes[AES_BLOCK_SIZE], const ACCEL_AES_KEY* srcKey);
    void accel_AES128_decrypt(uint8_t srcBytes[AES_BLOCK_SIZE], const ACCEL_AES_KEY* srcKey);
    void accel_AES128_set_key(const uint8_t srcUserKey[AES128_USERKEY_LENGTH], ACCEL_AES_KEY* dstKey);

#if defined(__cplusplus)
}
#endif

