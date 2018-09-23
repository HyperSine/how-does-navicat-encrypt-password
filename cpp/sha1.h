#pragma once
#include <stdint.h>
#include <stddef.h>

#if defined(__cplusplus)
extern "C" {
#endif

    typedef struct _ACCEL_SHA1_DIGEST {
        union {
            uint8_t byte[20];
            uint32_t dword[5];
        };
    } ACCEL_SHA1_DIGEST, ACCEL_SHA1_BUFFER;
    
    void accel_SHA1_init(ACCEL_SHA1_BUFFER* HashBuffer);

    // srcBytesLength must be a multiple of 64.
    void accel_SHA1_update(const void* __restrict srcBytes, 
                           size_t srcBytesLength, 
                           ACCEL_SHA1_BUFFER* __restrict HashBuffer);

    void accel_SHA1_final(const void* __restrict LeftBytes, 
                          size_t LeftBytesLength, 
                          uint64_t TotalBytesLength,
                          const ACCEL_SHA1_BUFFER* HashBuffer, ACCEL_SHA1_DIGEST* Hash);

    void accel_SHA1(const void* __restrict srcBytes, 
                    size_t srclen,
                    ACCEL_SHA1_DIGEST* __restrict Hash);

#if defined(__cplusplus)
}
#endif