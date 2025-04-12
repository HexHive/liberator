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
    size_t offset = 4;
    cJSON *a = NULL, *b = NULL;
    cJSON_bool case_sensitive;

    if(size <= offset) return 0;
    if(data[size-1] != '\0') return 0;
    if(data[0] != '1' && data[0] != '0') return 0;
    if(data[1] != '1' && data[1] != '0') return 0;

    case_sensitive = data[0] == '1' ? 1 : 0;

    a = cJSON_ParseWithOpts((const char*)data + offset, NULL, 0);
    if(a == NULL) return 0;

    offset += strlen((const char*)data + offset) + 1;
    if(offset >= size)
    {
        cJSON_Delete(a);
        return 0;
    }

    b = cJSON_ParseWithOpts((const char*)data + offset, NULL, 0);
    if(b == NULL)
    {
        cJSON_Delete(a);
        return 0;
    }

    cJSON_Compare(a, b, case_sensitive);

    cJSON_Delete(a);
    cJSON_Delete(b);

    return 0;
}

#ifdef __cplusplus
}
#endif
