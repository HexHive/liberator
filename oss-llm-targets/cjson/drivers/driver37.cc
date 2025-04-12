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
    char *string;
    size_t offset = 4;

    if(size <= offset) return 0;
    if(data[size-1] != '\0') return 0;
    if(data[0] != '1' && data[0] != '0') return 0;
    if(data[1] != '1' && data[1] != '0') return 0;
    if(data[2] != '1' && data[2] != '0') return 0;
    if(data[3] != '1' && data[3] != '0') return 0;

    if(data[0] == '1')
    {
        object = cJSON_ParseWithOpts((const char*)data + offset, NULL, 0);
        if(object == NULL) return 0;
    }
    else
    {
        object = cJSON_CreateObject();
        if(object == NULL) return 0;
    }

    if(data[1] == '1')
    {
        newitem = cJSON_ParseWithOpts((const char*)data + offset, NULL, 0);
        if(newitem == NULL)
        {
            cJSON_Delete(object);
            return 0;
        }
    }
    else
    {
        newitem = cJSON_CreateObject();
        if(newitem == NULL)
        {
            cJSON_Delete(object);
            return 0;
        }
    }

    if(data[2] == '1')
    {
        string = (char*)data + offset;
    }
    else
    {
        string = NULL;
    }

    cJSON_ReplaceItemInObjectCaseSensitive(object, string, newitem);

    cJSON_Delete(object);
    cJSON_Delete(newitem);

    return 0;
}

#ifdef __cplusplus
}
#endif
