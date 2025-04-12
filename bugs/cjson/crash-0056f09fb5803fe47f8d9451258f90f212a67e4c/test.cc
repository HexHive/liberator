#include <cjson/cJSON.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>


int main(int argc, char** argv) {

	cJSON *cjson_0 = nullptr;
	cJSON *cjson_1 = nullptr;

	int int_0 = 0;
	int int_1 = 0;
	int int_2 = 0;

	char *x = "\"XXXXX\"";

	cjson_0 =  cJSON_Parse(x);
	if (cjson_0 == 0)
        return 1;
	int_0 =  cJSON_AddItemReferenceToObject(cjson_0, "", cjson_0);
    printf("int_0: %d\n", int_0);
	cjson_1 =  cJSON_GetArrayItem(cjson_0, 0);
	if (cjson_1 == 0)
        return 1;
    printf("cjson_1: %s\n", cJSON_Print(cjson_1));
	int_1 =  cJSON_ReplaceItemInObject(cjson_0, "", cjson_0);
    printf("cjson_0: %s\n", cJSON_Print(cjson_0));
    printf("cjson_0: %p\ncjson_1: %p\n", cjson_0, cjson_1);
	int_2 =  cJSON_AddItemReferenceToObject(cjson_0, "", cjson_1); // bug here

    if (int_2 == 1)
        printf("success!\n");

    printf("end\n");

	return 0;
}