#include "xv_hscaler.h"

XV_hscaler_Config XV_hscaler_ConfigTable[] __attribute__ ((section (".drvcfg_sec"))) = {

	{
		"xlnx,v-hscaler-1.1", /* compatible */
		0x0, /* reg */
		0x1, /* xlnx,samples-per-clock */
		0x3, /* xlnx,num-video-components */
		0x500, /* xlnx,max-cols */
		0x2d0, /* xlnx,max-rows */
		0x8, /* xlnx,max-data-width */
		0x6, /* xlnx,phase-shift */
		0x2, /* xlnx,scale-mode */
		0x6, /* xlnx,taps */
		0x1, /* xlnx,enable-422 */
		0x1, /* xlnx,enable-420 */
		0x0 /* xlnx,enable-csc */
	},
	 {
		 NULL
	}
};