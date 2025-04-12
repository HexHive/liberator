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
	ucl_object_t *top;
	top = ucl_object_new();
	ucl_object_t *elt;
	elt = ucl_object_new();
	ucl_object_merge(top, elt, true);
	ucl_object_unref(elt);
	ucl_object_unref(top);
        return 0;
}

#ifdef __cplusplus
}
#endif
