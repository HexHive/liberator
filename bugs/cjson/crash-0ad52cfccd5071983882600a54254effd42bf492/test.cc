#include <cjson/cJSON.h>

#include <stdlib.h>
#include <stdint.h>

// issue link at https://github.com/DaveGamble/cJSON/issues/881

int main(int argc, char** argv) {
        
        cJSON *obj;
        cJSON *obj_dup;

        char* str;

        obj =  cJSON_Parse("\"fooz\"");
        
        obj_dup =  cJSON_Duplicate(obj, 1);
        if (obj_dup == 0) return 0;

        str = "aaaa";
        
        str =  cJSON_SetValuestring(obj_dup, "beeez");
        cJSON_SetValuestring(obj_dup, str);
        
        return 0;
}