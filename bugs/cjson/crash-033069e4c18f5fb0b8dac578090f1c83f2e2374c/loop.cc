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

    printf("json: %s\n", cJSON_Print(json));

    ret_v =  cJSON_ReplaceItemInArray(json, 0, json);
    if (ret_v == 0) 
        printf("Replace failed!\n");
    else
        printf("Replaced success!!\n");
    
    printf("end\n");

    cJSON_Delete(json);

    return 0;
}