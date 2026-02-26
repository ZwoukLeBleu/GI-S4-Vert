#include "scaler.h"
#include "myColorRegister.h"
#include "xparameters.h"
#include "sleep.h"
#include <string.h>
#include <xil_printf.h>
#include <xil_cache.h>


static uint32_t colorA = 0;

int main()
{
	configureScaler();

    uint32_t colorB = 0x00FF00; // RBG
    MYCOLORREGISTER_mWriteReg(XPAR_MYCOLORREGISTER_0_BASEADDR, 4, colorB);
    uint32_t reg2 = 0;
    while(1)
    {
    Xil_DCacheFlushRange((uint32_t)&colorA, sizeof(colorA));
    MYCOLORREGISTER_mWriteReg(XPAR_MYCOLORREGISTER_0_BASEADDR, 0, (uint32_t)&colorA);
    colorA = colorA + 1024;
    reg2 = MYCOLORREGISTER_mReadReg(XPAR_MYCOLORREGISTER_0_BASEADDR, 8);
    xil_printf("REG 2 : 0x%08X\n\r", reg2);
    xil_printf("REG 2 : 0x%08X\n\r", &colorA);
    sleep(1);
    }

    return 0;
}
