#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>

#include "library.h"

extern "C" {

typedef struct _codec {
	struct _codec* next;
	TIFFCodec* info;
} codec_t;
static codec_t* registeredCODECS = NULL;

void my_free(void* s) {
	free(s);
}

void* my_malloc(size_t s) {
	if (s == 0)
		return NULL;

	return malloc(s);
}

TIFFCodec*
TIFFRegisterCODEC(uint16_t scheme, const char* name)
{
	codec_t* cd = (codec_t*)
	    my_malloc((size_t)(sizeof (codec_t) + sizeof (TIFFCodec) + strlen(name)+1));

	if (cd != NULL) {
		cd->info = (TIFFCodec*) ((uint8_t*) cd + sizeof (codec_t));
		cd->info->name = (char*)
		    ((uint8_t*) cd->info + sizeof (TIFFCodec));
		strcpy(cd->info->name, name);
		cd->info->scheme = scheme;
		cd->next = registeredCODECS;
		registeredCODECS = cd;
	} else {
		return NULL;
	}
	return (cd->info);

	// TIFFCodec* cd = (TIFFCodec*)my_malloc(sizeof(TIFFCodec));
	// return cd;
}

}