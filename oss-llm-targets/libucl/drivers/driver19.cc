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
	struct ucl_parser *parser;
       	parser = ucl_parser_new(0);
	
	ucl_parser_add_string(parser, (char *)data, size);
	
	if (ucl_parser_get_error(parser) != NULL) {
		return 0;
	}
	ucl_object_t * obj;
	obj = ucl_parser_get_current_stack_object(parser, 0);
	ucl_object_iter_t it;
	void* a, *b, *c;
	ucl_object_iterate_with_error(obj, &it, false, NULL);
	ucl_parser_free (parser);
        return 0;
}

#ifdef __cplusplus
}
#endif
