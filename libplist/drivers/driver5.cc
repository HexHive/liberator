#include <plist/plist.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>

#define FIXED_SIZE 8
#define COUNTER_NUMBER 0
#define MIN_SEED_SIZE 8
const unsigned counter_size[COUNTER_NUMBER] = {  };

#define NEW_DATA_LEN 4096


#define MIN(x,y) ((x < y) ? x : y)


extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t Size) {
	if (Size < MIN_SEED_SIZE) return 0;
	void *void_p_h0[1] = { 0 };
	void *void_p_h0_shadow[1] = { 0 };
	double double_s0[1];
	memset(double_s0, 0x0, sizeof(double_s0));
	memcpy(double_s0, data, sizeof(double_s0));data += sizeof(double_s0);
	void_p_h0[0] =  plist_new_real(double_s0[0]);
	if (void_p_h0[0] == 0) goto clean_up;

clean_up:
	if (void_p_h0_shadow[0] != 0) plist_free(void_p_h0[0]);

	return 0;
}