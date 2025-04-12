#include <library.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t Size) {
	int int_s0[1]; // x
	char *char_p_h2[128]; // x
	int int_s3[1]; // x
	char *char_p_s0 = "rwosdlqqzuubrqpbuulq.bin"; // x
	int int_s2[1]; // x
	my_struct *my_struct_p_h0[1];
	int int_s1[1]; // x
	char *char_p_h1[128]; // x
	size_t size_t_s0[1]; // x
	void *void_p_h0[1]; // x

	if (Size == 0)
		return 0;

	memcpy(int_s0, data, sizeof(int_s0));data += sizeof(int_s0);
	memcpy(int_s1, data, sizeof(int_s1));data += sizeof(int_s1);
	//file init
	memcpy(size_t_s0, data, sizeof(size_t_s0));data += sizeof(size_t_s0);
	FILE *p0 = fopen(char_p_s0, "w");
	fwrite(data, 1, size_t_s0[0], p0);
	fclose(p0);data += size_t_s0[0];

	//dyn array init
	memcpy(int_s2, data, sizeof(int_s2));data += sizeof(int_s2);
	char_p_h1[0] = (char*)malloc(int_s2[0]);
	memcpy(char_p_h1[0], data, int_s2[0]);
	data += int_s2[0];

	//dyn array init
	memcpy(int_s3, data, sizeof(int_s3));data += sizeof(int_s3);
	char_p_h2[0] = (char*)malloc(int_s3[0]);
	memcpy(char_p_h2[0], data, int_s3[0]);
	data += int_s3[0];

	void_p_h0[0] =  my_malloc(int_s0[0]);
	if (void_p_h0[0] == 0) return 0;
	my_free(void_p_h0[0]);
	my_struct_p_h0[0] =  create(char_p_s0);
	if (my_struct_p_h0[0] == 0) return 0;
	operation(my_struct_p_h0[0]);
	set_b(my_struct_p_h0[0], int_s1[0]);
	set_b(my_struct_p_h0[0], int_s1[0]);
	set_data(my_struct_p_h0[0], char_p_h1[0], int_s2[0]);
	set_data(my_struct_p_h0[0], char_p_h2[0], int_s3[0]);
	get_data(my_struct_p_h0[0], char_p_h1[0]);
	operation(my_struct_p_h0[0]);

	return 0;
}