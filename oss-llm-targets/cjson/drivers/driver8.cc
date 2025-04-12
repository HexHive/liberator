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
    cJSON *json;
    cJSON *new_json;
    size_t offset = 4;
    unsigned char *copied;
    int recurse;

    if(size <= offset) return 0;
    if(data[size-1] != '\0') return 0;
    if(data[0] != '1' && data[0] != '0') return 0;
    if(data[1] != '1' && data[1] != '0') return 0;

    recurse = data[0] == '1' ? 1 : 0;

    json = cJSON_ParseWithOpts((const char*)data + offset, NULL, 1);

    if(json == NULL) return 0;

    new_json = cJSON_Duplicate(json, recurse);

    if(new_json == NULL)
    {
        cJSON_Delete(json);
        return 0;
    }

    copied = (unsigned char*)malloc(size);
    if(copied == NULL)
    {
        cJSON_Delete(json);
        cJSON_Delete(new_json);
        return 0;
    }

    memcpy(copied, data, size);

    cJSON_Minify((char*)copied + offset);

    free(copied);

    cJSON_Delete(json);

    cJSON_Delete(new_json);

    return 0;
}

#ifdef __cplusplus
}
#endif
