#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>
#include "library.h"

void TIFFFlush(TIFF* tif) {
   tif->tif_flags = 3;
}

void TIFFFreeDirectory(TIFF* tif) {
   tif->tif_flags = 5;
}

void _TIFFfree(void* p) {
   free(p);
}

#define O_RDONLY 10

void api1(TIFF* tif)
{
	/*
         * Flush buffered data and directory (if dirty).
         */
	if (tif->tif_mode != O_RDONLY)
		TIFFFlush(tif);
	// (*tif->tif_cleanup)(tif);
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
}
