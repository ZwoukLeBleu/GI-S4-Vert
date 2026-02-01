#include "SDHal.h"

uint8_t SD_HAL_init()
{
    hal.status = SD_HAL_INIT_STATUS;
    return 0;
}

uint32_t SD_HAL_readBytes(uint8_t *arr, uint32_t len)
{
    return 0;
}
