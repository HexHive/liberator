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
    int minify, require_termination, formatted, buffered;


    if(size <= offset) return 0;
    if(data[size-1] != '\0') return 0;
    if(data[0] != '1' && data[0] != '0') return 0;
    if(data[1] != '1' && data[1] != '0') return 0;
    if(data[2] != '1' && data[2] != '0') return 0;
    if(data[3] != '1' && data[3] != '0') return 0;

    minify              = data[0] == '1' ? 1 : 0;
    require_termination = data[1] == '1' ? 1 : 0;
    formatted           = data[2] == '1' ? 1 : 0;
    buffered            = data[3] == '1' ? 1 : 0;

    json = cJSON_ParseWithLength((const char*)data + offset, size - offset);

    if(json == NULL) return 0;

    if(minify)
    {
        copied = (unsigned char*)malloc(size);
        if(copied == NULL) return 0;

        memcpy(copied, data, size);

        cJSON_Minify((char*)copied + offset);

        free(copied);
    }

    cJSON_Delete(json);

    return 0;
}

#ifdef __cplusplus
}
#endif
