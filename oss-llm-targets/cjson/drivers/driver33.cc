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
    cJSON *object = NULL;
    cJSON *newitem = NULL;
    size_t offset = 4;
    unsigned char *copied;
    char *string = NULL;

    if(size <= offset) return 0;
    if(data[size-1] != '\0') return 0;
    if(data[0] != '1' && data[0] != '0') return 0;
    if(data[1] != '1' && data[1] != '0') return 0;
    if(data[2] != '1' && data[2] != '0') return 0;
    if(data[3] != '1' && data[3] != '0') return 0;

    object = cJSON_ParseWithOpts((const char*)data + offset, NULL, 0);

    if(object == NULL) return 0;

    if(data[0] == '1')
    {
        copied = (unsigned char*)malloc(size);
        if(copied == NULL) return 0;

        memcpy(copied, data, size);

        cJSON_Minify((char*)copied + offset);

        newitem = cJSON_ParseWithOpts((const char*)copied + offset, NULL, 0);

        free(copied);
    }
    else
    {
        newitem = cJSON_ParseWithOpts((const char*)data + offset, NULL, 0);
    }

    if(newitem == NULL) goto end;

    if(data[1] == '1')
    {
        string = cJSON_PrintUnformatted(object);
    }
    else
    {
        /* unbuffered printing */
        string = cJSON_PrintUnformatted(object);
    }

    if(string != NULL) free(string);

    if(data[2] == '1')
    {
        copied = (unsigned char*)malloc(size);
        if(copied == NULL) goto end;

        memcpy(copied, data, size);

        cJSON_Minify((char*)copied + offset);

        cJSON_ReplaceItemInObjectCaseSensitive(object, (const char*)copied + offset, newitem);

        free(copied);
    }
    else
    {
        cJSON_ReplaceItemInObjectCaseSensitive(object, (const char*)data + offset, newitem);
    }

end:
    cJSON_Delete(object);
    cJSON_Delete(newitem);

    return 0;
}

#ifdef __cplusplus
}
#endif
