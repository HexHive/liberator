#include <cjson/cJSON.h>

#include <stdlib.h>
#include <stdint.h>

int main(int argc, char** argv) {

	cJSON *a, *b;

	a =  cJSON_ParseWithOpts("\"foo\"", nullptr, 0);
	b =  cJSON_ParseWithOpts("\"bar\"", nullptr, 0);
	
	cJSON_DetachItemViaPointer(b, a);

	return 0;
}