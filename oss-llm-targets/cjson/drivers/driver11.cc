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

    if(size == 0) return 0;

    json = cJSON_Parse((const char*)data);

    if(json == NULL) return 0;

    cJSON_Delete(json);

    return 0;
}

#ifdef __cplusplus
}
#endif
