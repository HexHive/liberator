
#include <stdlib.h>
#include <inttypes.h>

extern "C" {

typedef struct {
	char* name;
	uint16_t scheme;
	// TIFFInitMethod init;
} TIFFCodec;

TIFFCodec* TIFFRegisterCODEC(uint16_t, const char*);

}