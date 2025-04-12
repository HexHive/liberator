#include <library.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>

#define FIXED_SIZE 640
#define COUNTER_NUMBER 0
#define MIN_SEED_SIZE 640
const unsigned counter_size[COUNTER_NUMBER] = {  };

#define NEW_DATA_LEN 4096


extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t Size) {
	if (Size < MIN_SEED_SIZE) return 0;
	char char_p_s4[128];
	char char_p_s3[128];
	char char_p_s2[128];
	char *char_pp_g1[1][1] = { 0 };
	char char_p_s1[128];
	char char_p_s0[128];
	char *char_pp_g0[1][1] = { 0 };
	memcpy(char_p_s4, data, sizeof(char_p_s4));data += sizeof(char_p_s4);
	char_p_s4[sizeof(char_p_s4) - 1] = 0;
	memcpy(char_p_s3, data, sizeof(char_p_s3));data += sizeof(char_p_s3);
	char_p_s3[sizeof(char_p_s3) - 1] = 0;
	memcpy(char_p_s2, data, sizeof(char_p_s2));data += sizeof(char_p_s2);
	char_p_s2[sizeof(char_p_s2) - 1] = 0;
	memcpy(char_p_s1, data, sizeof(char_p_s1));data += sizeof(char_p_s1);
	char_p_s1[sizeof(char_p_s1) - 1] = 0;
	memcpy(char_p_s0, data, sizeof(char_p_s0));data += sizeof(char_p_s0);
	char_p_s0[sizeof(char_p_s0) - 1] = 0;
	bar(char_p_s0);
	foo(char_p_s0);
	bar(char_p_s1);
	foo(char_pp_g0[0]);
	bar(char_p_s2);
	foo(char_p_s2);
	bar(char_p_s3);
	bar(char_p_s4);
	foo(char_pp_g1[0]);
	bar(char_p_s2);

	return 0;
}