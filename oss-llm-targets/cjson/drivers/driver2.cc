#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

#include <cjson/cJSON.h>

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size); /* required by C89 */

int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size)
{
    cJSON *a = cJSON_Parse((const char*)data);
    cJSON *b = cJSON_Parse((const char*)data);
    if(a == NULL || b == NULL) return 0;

    cJSON_Compare(a, b, 0);
    cJSON_Compare(a, b, 1);

    cJSON_Delete(a);
    cJSON_Delete(b);

    return 0;
}

#ifdef __cplusplus
}
#endif
