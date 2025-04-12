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
    cJSON *object;
    cJSON *newitem;
    size_t offset = 4;
    size_t object_size;
    size_t newitem_size;
    char *object_string = NULL;
    char *newitem_string = NULL;
    cJSON_bool result;

    if(size <= offset) return 0;
    if(data[size-1] != '\0') return 0;
    if(data[0] != '1' && data[0] != '0') return 0;
    if(data[1] != '1' && data[1] != '0') return 0;
    if(data[2] != '1' && data[2] != '0') return 0;
    if(data[3] != '1' && data[3] != '0') return 0;

    object_size = data[0] == '1' ? 1 : 0;
    newitem_size = data[1] == '1' ? 1 : 0;
    object_string = (char*)malloc(object_size);
    newitem_string = (char*)malloc(newitem_size);

    if(object_size > 0)
    {
        memcpy(object_string, data + offset, object_size);
        object = cJSON_Parse(object_string);
        if(object == NULL) return 0;
    }
    else
    {
        object = cJSON_CreateObject();
    }

    if(newitem_size > 0)
    {
        memcpy(newitem_string, data + offset + object_size, newitem_size);
        newitem = cJSON_Parse(newitem_string);
        if(newitem == NULL) return 0;
    }
    else
    {
        newitem = cJSON_CreateObject();
    }

    result = cJSON_ReplaceItemInObjectCaseSensitive(object, "test", newitem);

    cJSON_Delete(object);
    cJSON_Delete(newitem);

    if(object_string != NULL) free(object_string);
    if(newitem_string != NULL) free(newitem_string);

    return 0;
}

#ifdef __cplusplus
}
#endif
