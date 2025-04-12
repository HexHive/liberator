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
    cJSON *object, *newitem;
    size_t offset = 4;
    unsigned char *copied;

    if(size <= offset) return 0;
    if(data[size-1] != '\0') return 0;
    if(data[0] != '1' && data[0] != '0') return 0;
    if(data[1] != '1' && data[1] != '0') return 0;
    if(data[2] != '1' && data[2] != '0') return 0;
    if(data[3] != '1' && data[3] != '0') return 0;

    object = cJSON_ParseWithOpts((const char*)data + offset, NULL, data[0] == '1' ? 1 : 0);

    if(object == NULL) return 0;

    copied = (unsigned char*)malloc(size);
    if(copied == NULL) return 0;

    memcpy(copied, data, size);

    newitem = cJSON_ParseWithOpts((const char*)copied + offset, NULL, data[1] == '1' ? 1 : 0);

    if(newitem == NULL) return 0;

    cJSON_ReplaceItemInObjectCaseSensitive(object, (const char*)copied + offset + size, newitem);

    cJSON_Delete(object);
    cJSON_Delete(newitem);
    free(copied);

    return 0;
}

#ifdef __cplusplus
}
#endif
