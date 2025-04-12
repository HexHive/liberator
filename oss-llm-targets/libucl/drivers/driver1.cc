#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include "ucl.h"
#ifdef __cplusplus
extern "C" {
#endif

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
	// If size is 0 we need a null-terminated string.
	// We dont null-terminate the string and by the design
	// of the API passing 0 as size with non null-terminated string
	// gives undefined behavior. 	
	if(size==0){
		return 0;
	}
	ucl_object_t *top = ucl_object_new();
	ucl_object_t *elt = ucl_object_new();
	ucl_array_merge(top, elt, false);
	
	if (ucl_parser_get_error((ucl_parser *)top) != NULL) {
		return 0;
	}

	ucl_object_free(top);
	ucl_object_free(elt);
        return 0;
}

#ifdef __cplusplus
}
#endif
