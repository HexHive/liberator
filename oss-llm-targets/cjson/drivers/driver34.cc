#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

#include <cjson/cJSON.h>

int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size); /* required by C89 */

int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size)
{
    char *string = NULL;
    cJSON *object = NULL;
    cJSON *newitem = NULL;
    int ret;

    if(size <= 4) return 0;
    if(data[size-1] != '\0') return 0;

    string = (char*)malloc(size);
    if(string == NULL) return 0;
    memcpy(string, data, size);
    string[size-1] = '\0';

    object = cJSON_Parse(string);
    if(object == NULL) goto end;

    newitem = cJSON_Parse(string);
    if(newitem == NULL) goto end;

    ret = cJSON_ReplaceItemInObjectCaseSensitive(object, string, newitem);
    if(ret == 0) goto end;

end:
    free(string);
    cJSON_Delete(object);
    cJSON_Delete(newitem);

    return 0;
}

#ifdef __cplusplus
}
#endif
