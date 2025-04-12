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
    cJSON *object, *item, *newitem;
    size_t offset = 4;
    char *string;

    if(size <= offset) return 0;
    if(data[size-1] != '\0') return 0;
    if(data[0] != '1' && data[0] != '0') return 0;
    if(data[1] != '1' && data[1] != '0') return 0;
    if(data[2] != '1' && data[2] != '0') return 0;
    if(data[3] != '1' && data[3] != '0') return 0;

    string = (char*)data + offset;

    object = cJSON_Parse((const char*)data + offset);
    if(object == NULL) return 0;

    item = cJSON_GetObjectItemCaseSensitive(object, string);
    if(item == NULL) return 0;

    newitem = cJSON_CreateNull();

    cJSON_ReplaceItemInObjectCaseSensitive(object, string, newitem);

    cJSON_Delete(object);

    return 0;
}

#ifdef __cplusplus
}
#endif
