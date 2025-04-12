#include <tiffio.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>


int main() {
	TIFFCIELabToRGB lab2rgb;
	float x,y,z;
	x = 0;
	y = 0;
	z = 0;
	TIFFDisplay display = {
		{   /* XYZ -> luminance matrix */
			{  3.2410F, -1.5374F, -0.4986F },
			{  -0.9692F, 1.8760F, 0.0416F },
			{  0.0556F, -0.2040F, 1.0570F }
		},
		100.0F, 100.0F, 100.0F, /* Light o/p for reference white */
		255, 255, 255,          /* Pixel values for ref. white */
		100.F, 100.0F, 100.0F,       /* Residual light o/p for black pixel */
		2.4F, 2.4F, 2.4F,       /* Gamma values for the three guns */
	};
	float w[3] = {0, 0,0};
	TIFFCIELabToRGBInit(&lab2rgb, &display, w);
	TIFFCIELabToXYZ(&lab2rgb, 0xc104, 0x9e843e5, 0x544fa337, &x,&y,&z);
	uint32_t r,g,b;
	TIFFXYZToRGB(&lab2rgb, x, y, z, &r, &g, &b);

	return 0;
}
