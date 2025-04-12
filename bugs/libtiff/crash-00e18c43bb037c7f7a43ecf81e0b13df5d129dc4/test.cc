#include <tiffio.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>


int main(int argc, char** argv) {

	__uint32_t w = 0x5a158d1;
 	__uint32_t h = 0x1;

	uint32_t *raster = (uint32_t*)malloc(w*h);

	TIFF *atiff = nullptr;

	char *file_path = "image.tiff";

	atiff =  TIFFOpen(file_path, "w");
	if (atiff == 0)
		return 1;

	TIFFCheckpointDirectory(atiff);
	TIFFReadRGBAImage(atiff, w, h, raster, 0x1);

    printf("end\n");

	free(raster);
	TIFFClose(atiff);

	return 0;
}