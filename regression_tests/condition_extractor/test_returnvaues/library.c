#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>
#include "library.h"


#define O_RDONLY 10
#define FIELD_CUSTOM    65

#define TIFF_MYBUFFER    0x00200U /* my raw data buffer; free on close */
#define TIFF_ISTILED     0x00400U /* file is tile, not strip- based */
#define TIFF_MAPPED      0x00800U /* file is mapped into memory */

#define isMapped(tif) (((tif)->tif_flags & TIFF_MAPPED) != 0)

#define TIFFUnmapFileContents(tif, addr, size) \
	((*(tif)->tif_unmapproc)((tif)->tif_clientdata,(addr),(size)))

static void
_tiffDummyUnmapProc(void* fd, void* base, uint32_t size)
{
	(void) fd; (void) base; (void) size;
}

int TIFFFlush(TIFF* tif)
{
    if( tif->tif_mode == O_RDONLY )
        return 1;
	return 0;
}

void _TIFFfree(void* p) {
   free(p);
}


static void
LogLuvCleanup(TIFF* tif)
{
	tif->tif_mode = 0;
}

TIFF* api1(int fd, int mode, int flags, char* name)
{

	TIFF* s = (TIFF*)malloc(sizeof(TIFF));

	if (name == NULL) {
		s->tif_flags = flags;

		return (TIFF*)0;
	} else {
		s->tif_fd = fd;
		s->tif_mode = mode;

		return s;
	}
}
