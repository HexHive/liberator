#include <cjson/cJSON.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>


int main(int argc, char** argv) {

	cJSON *cjson_0 = nullptr;
	cJSON *cjson_1 = nullptr;
	cJSON *cjson_2 = nullptr;

	int int_0 = 0;
	int int_1 = 0;
	int int_2 = 0;

	// char *x = "992222.22222";

	// cjson_0 =  cJSON_Parse(x); // allocated here
	// if (cjson_0 == 0)
	// 	return 0;
	// printf("cJSON_p_g0: %s\n", cJSON_Print(cjson_0));
	// printf("cJSON_p_g0: %p\n", cjson_0);
	// cjson_1 =  cJSON_CreateObjectReference(cjson_0);
	// printf("cJSON_p_g1: %p\n", cjson_1);
	// if (cjson_1 == 0)
	// 	return 0;
	// int_1 =  cJSON_AddItemToObjectCS(cjson_1, "", cjson_1);
	// printf("int_s1: %d\n", int_1);
	// printf("cJSON_p_g1: %s\n", cJSON_Print(cjson_1));
	// int_0 =  cJSON_ReplaceItemInObjectCaseSensitive(cjson_0, "", cjson_1);
	// printf("int_s0: %d\n", int_0);
	// printf("cJSON_p_g0: %s\n", cJSON_Print(cjson_0));
	// cJSON_DeleteItemFromArray(cjson_1, 0); // delete here
	// printf("int_s0[0]: %d\n", int_0);
	// printf("cJSON_p_g1: %s\n", cJSON_Print(cjson_1));
	// cjson_2 =  cJSON_CreateObjectReference(cjson_0);
	// if (cjson_2 == 0) 
	// 	return 0;
	// int_2 =  cJSON_AddItemToObject(cjson_2, "", cjson_1); // bug

	// printf("end\n");

	char *x = "{\"\": 992222.22222}";

	cjson_0 =  cJSON_Parse(x); // allocated here
	if (cjson_0 == 0)
		return 1;
	printf("cjson_0: %s\n", cJSON_Print(cjson_0));
	cJSON_DeleteItemFromArray(cjson_0, 0);
	printf("cjson_0: %s\n", cJSON_Print(cjson_0));
	cJSON_Delete(cjson_0);
	printf("this should not happens\nend\n");

	return 0;
}