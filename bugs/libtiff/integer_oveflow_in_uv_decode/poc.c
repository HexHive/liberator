#include <tiffio.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>



int main() {
	uv_encode(0x7fffffffffffffff, 0x8000000000000000, 0x3b287831);
}
