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

void api1(TIFF* tif)
{
	/*
         * Flush buffered data and directory (if dirty).
         */
	if (tif->tif_mode != O_RDONLY)
		TIFFFlush(tif);
	(*tif->tif_cleanup)(tif);
	// TIFFFreeDirectory(tif);

	if (tif->tif_dirlist)
		_TIFFfree(tif->tif_dirlist);

	/*
         * Clean up client info links.
         */
	while( tif->tif_clientinfo )
	{
		TIFFClientInfoLink *psLink = tif->tif_clientinfo;

		tif->tif_clientinfo = psLink->next;
		_TIFFfree( psLink->name );
		_TIFFfree( psLink );
	}

	if (tif->tif_rawdata && (tif->tif_flags&TIFF_MYBUFFER))
		_TIFFfree(tif->tif_rawdata);
	if (isMapped(tif))
		TIFFUnmapFileContents(tif, tif->tif_base, 0);

	/*
         * Clean up custom fields.
         */
	if (tif->tif_fields && tif->tif_nfields > 0) {
		uint32_t i;

		for (i = 0; i < tif->tif_nfields; i++) {
			TIFFField *fld = tif->tif_fields[i];
			if (fld->field_bit == FIELD_CUSTOM &&
			    strncmp("Tag ", fld->field_name, 4) == 0) {
				_TIFFfree(fld->field_name);
				_TIFFfree(fld);
			}
		}

		_TIFFfree(tif->tif_fields);
	}

        if (tif->tif_nfieldscompat > 0) {
                uint32_t i;

                for (i = 0; i < tif->tif_nfieldscompat; i++) {
                        if (tif->tif_fieldscompat[i].allocated_size)
                                _TIFFfree(tif->tif_fieldscompat[i].fields);
                }
                _TIFFfree(tif->tif_fieldscompat);
        }

	_TIFFfree(tif);
}
