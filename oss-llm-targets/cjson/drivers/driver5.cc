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
    cJSON *a = NULL, *b = NULL;
    size_t offset = 4;
    unsigned char *copied;
    char *printed_json = NULL;
    int minify, require_termination, formatted, buffered;
    cJSON_bool case_sensitive;


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
    case_sensitive      = data[4] == '1' ? 1 : 0;

    a = cJSON_ParseWithOpts((const char*)data + offset, NULL, require_termination);
    b = cJSON_ParseWithOpts((const char*)data + offset, NULL, require_termination);

    if(a == NULL) return 0;
    if(b == NULL) return 0;

    if(buffered)
    {
        printed_json = cJSON_PrintBuffered(a, 1, formatted);
    }
    else
    {
        /* unbuffered printing */
        if(formatted)
        {
            printed_json = cJSON_Print(a);
        }
        else
        {
            printed_json = cJSON_PrintUnformatted(a);
        }
    }

    if(printed_json != NULL) free(printed_json);

    if(minify)
    {
        copied = (unsigned char*)malloc(size);
        if(copied == NULL) return 0;

        memcpy(copied, data, size);

        cJSON_Minify((char*)copied + offset);

        free(copied);
    }

    cJSON_Delete(a);
    cJSON_Delete(b);

    cJSON_Compare(a, b, case_sensitive);

    return 0;
}

#ifdef __cplusplus
}
#endif
