#include <tiffio.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>



int main() {
	TIFF* tif =  TIFFOpen("poc.tiff", "rh");
	if (tif == 0) return 1;
	int offset = 4;
	TIFFReadGPSDirectory(tif, offset);
	return 0;
}
