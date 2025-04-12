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
    size_t offset = 4;
    unsigned char *copied;
    cJSON *duplicated_json = NULL;
    cJSON_bool recurse;


    if(size <= offset) return 0;
    if(data[size-1] != '\0') return 0;
    if(data[0] != '1' && data[0] != '0') return 0;
    if(data[1] != '1' && data[1] != '0') return 0;
    if(data[2] != '1' && data[2] != '0') return 0;
    if(data[3] != '1' && data[3] != '0') return 0;

    recurse = data[0] == '1' ? 1 : 0;

    json = cJSON_ParseWithOpts((const char*)data + offset, NULL, 0);

    if(json == NULL) return 0;

    duplicated_json = cJSON_Duplicate(json, recurse);

    if(duplicated_json != NULL) cJSON_Delete(duplicated_json);

    cJSON_Delete(json);

    return 0;
}

#ifdef __cplusplus
}
#endif
