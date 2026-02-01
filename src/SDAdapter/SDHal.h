#pragma once

#include <stdint.h>

#define SD_HAL_INIT_STATUS 0
#define SD_HAL_READY_STATUS 1
#define SD_HAL_BUSY_STATUS 2
#define SD_HAL_ERROR_STATUS 3

typedef struct {
    uint32_t errorRegister;
    uint8_t status;
} SD_HAL;

/// @brief This function initializes the SD reader.
/// @return Returns 0 if the SD failed (Error Register from hal instance updated) or 1 if ready
uint8_t SD_HAL_init();

/// @brief This function reads raw bytes from the file. the hal needs to be set as READY before reading.
/// @param arr The array sized at len
/// @param len the number of bytes to read
/// @return 0 if failed (Error Register from hal instance updated) or the number of bytes read
uint32_t SD_HAL_readBytes(uint8_t *arr, uint32_t len);

static SD_HAL hal;