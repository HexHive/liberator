#include <cjson/cJSON.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>


int main(int argn, char** argc) {

    int ret_v;
    cJSON *json;
    
    // char *x = "[[[[true]]]]";
    char *x = "[true]";
    char *e = "";

    printf("start\n");

    json =  cJSON_ParseWithLength(x, strlen(x)+1);
    if (json == 0) {
        printf("error 1\n");
        return 0;
    }

    printf("d: %s\n", cJSON_Print(json));
    // ret_v =  cJSON_ReplaceItemInObjectCaseSensitive(json, char_p_h0[0], json);
    // ret_v =  cJSON_ReplaceItemInObjectCaseSensitive(json, e, json);
    // if (ret_v == 0) 
    //     printf("Replace failed!\n");
    printf("e: %s\n", cJSON_Print(json));
    // printf("i: %d\n", ret_v);
    ret_v =  cJSON_ReplaceItemInArray(json, 0, json);
    if (ret_v == 0) 
        printf("Replace failed!\n");
    // printf("f: %s\n", cJSON_Print(json));
    // cJSON_DeleteItemFromObject(json, e);
    // printf("g: %s\n", cJSON_Print(json));
    // printf("c1: %s\n", e);
    // ret_v =  cJSON_ReplaceItemInObjectCaseSensitive(json, e, json);
    // ret_v =  cJSON_ReplaceItemInObjectCaseSensitive(json, e, json);

    printf("end\n");

    cJSON_Delete(json);

    return 0;
}