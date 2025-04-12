#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

#include <cjson/cJSON.h>

int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size); /* required by C89 */

int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size)
{
    cJSON *json;
    cJSON *json2;
    cJSON_bool case_sensitive;


    if(size <= 1) return 0;
    if(data[0] != '1' && data[0] != '0') return 0;
    if(data[1] != '1' && data[1] != '0') return 0;

    case_sensitive = data[0] == '1' ? 1 : 0;

    json = cJSON_Parse((const char*)data + 2);
    if(json == NULL) return 0;

    json2 = cJSON_Parse((const char*)data + size/2);
    if(json2 == NULL) return 0;

    cJSON_Compare(json, json2, case_sensitive);

    cJSON_Delete(json);
    cJSON_Delete(json2);

    return 0;
}

#ifdef __cplusplus
}
#endif
