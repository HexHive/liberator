#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <ucl.h>
#include <ctype.h>
#ifdef __cplusplus
extern "C" {
#endif

typedef ucl_object_t* (*ucl_msgpack_test)(void);


int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
	
	if(size<3){
		return 0;
	}

	ucl_object_t *obj = ucl_object_new_full (UCL_OBJECT, 2);
	obj->type = UCL_OBJECT;
	
	char *key = (char*)data;
	size_t keylen = size;
	bool copy_key = 1;

	ucl_object_replace_key(obj, obj, key, keylen, copy_key);

	ucl_object_unref(obj);
	return 0;
}





#ifdef __cplusplus
}
#endif
