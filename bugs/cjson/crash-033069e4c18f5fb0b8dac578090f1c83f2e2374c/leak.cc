#include <cjson/cJSON.h>

#include <string.h>
#include <stdio.h>

int main(int argn, char** argc) {

    int ret_v;
    cJSON *json;
    
    char *x = "[true]";
    
    printf("start\n");

    json =  cJSON_ParseWithLength(x, strlen(x)+1);
    if (json == 0) {
        printf("error 1\n");
        return 0;
    }

    while (true) {
        printf("json: %s\n", cJSON_Print(json));
    }
    
    printf("end\n");

    cJSON_Delete(json);

    return 0;
}