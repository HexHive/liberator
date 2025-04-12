#include <library.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>

#define FIXED_SIZE 6
#define COUNTER_NUMBER 0
#define MIN_SEED_SIZE 6
const unsigned counter_size[COUNTER_NUMBER] = {  };

#define NEW_DATA_LEN 4096


extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t Size) {
	if (Size < MIN_SEED_SIZE) return 0;
	short short_s0[1];
	a_context_t a_context_t_p_s0[1];
	int int_s0[1];
	iface_t *iface_t_p_g0[1] = { 0 };
	memcpy(short_s0, data, sizeof(short_s0));data += sizeof(short_s0);
	memcpy(int_s0, data, sizeof(int_s0));data += sizeof(int_s0);
	iface_t_p_g0[0] =  get_a_struct();
	if (iface_t_p_g0[0] == 0) return 0;
	init_a_context(iface_t_p_g0[0], a_context_t_p_s0, int_s0[0], short_s0[0]);
	fake_init(iface_t_p_g0[0], a_context_t_p_s0);

	return 0;
}