#include <aom/aom_image.h>
#include <aom/aom_decoder.h>
#include <aom/aom.h>
#include <aom/aomcx.h>
#include <aom/aom_codec.h>
#include <aom/aom_integer.h>
#include <aom/aom_encoder.h>
#include <aom/aomdx.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>

#define FIXED_SIZE 3085
#define COUNTER_NUMBER 1
#define MIN_SEED_SIZE 3093
const unsigned counter_size[COUNTER_NUMBER] = { 8 };

#define NEW_DATA_LEN 4096


#define MIN(x,y) ((x < y) ? x : y)


int f195ae08f (void *, size_t, aom_codec_frame_buffer_t *) {
	return (int)0;
}

int fbb19e6c8 (void *, aom_codec_frame_buffer_t *) {
	return (int)0;
}


extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t Size) {
	if (Size < MIN_SEED_SIZE) return 0;
	char char_p_s5[128];
	aom_codec_iter_t aom_codec_iter_t_p_s0[128];
	aom_metadata_insert_flags aom_metadata_insert_flags_s0[1];
	aom_codec_ctx_t aom_codec_ctx_t_p_s0[1];
	aom_codec_ctx_t aom_codec_ctx_t_p_s3[128];
	aom_codec_err_t aom_codec_err_t_s7[1];
	aom_image_t *aom_image_t_p_g0[1] = { 0 };
	aom_codec_stream_info_t aom_codec_stream_info_t_p_s0[1];
	unsigned long unsignedlong_s0[1];
	char char_p_s3[128];
	long long_s0[1];
	aom_codec_err_t aom_codec_err_t_s5[1];
	aom_codec_err_t aom_codec_err_t_s0[1];
	aom_codec_ctx_t aom_codec_ctx_t_p_s2[128];
	aom_image_t *aom_image_t_p_h2[1] = { 0 };
	aom_codec_ctx_t aom_codec_ctx_t_p_s1[128];
	unsigned int unsignedint_s3[1];
	aom_codec_err_t aom_codec_err_t_s4[1];
	aom_image_t *aom_image_t_p_g6[1] = { 0 };
	aom_codec_iface_t *aom_codec_iface_t_p_g0[1] = { 0 };
	char char_p_s1[128];
	char char_p_s4[128];
	char char_p_s6[128];
	aom_codec_err_t aom_codec_err_t_s3[1];
	aom_image_t *aom_image_t_p_g1[1] = { 0 };
	const char *char_p_cg1[1] = { 0 };
	unsigned int unsignedint_s2[1];
	char char_p_s2[128];
	aom_codec_err_t aom_codec_err_t_s8[1];
	aom_fixed_buf_t *aom_fixed_buf_t_p_h0[1] = { 0 };
	aom_codec_dec_cfg_t aom_codec_dec_cfg_t_p_s0[1];
	aom_image_t *aom_image_t_p_h5[1] = { 0 };
	OBU_TYPE OBU_TYPE_s0[1];
	const aom_codec_cx_pkt_t *aom_codec_cx_pkt_t_p_cg1[1] = { 0 };
	__uint32_t __uint32_t_s0[1];
	const char *char_p_cg0[1] = { 0 };
	aom_img_fmt aom_img_fmt_s0[1];
	char char_p_s0[128];
	unsigned int unsignedint_s0[1];
	int64_t int64_t_s0[1];
	aom_codec_enc_cfg_t aom_codec_enc_cfg_t_p_s0[1];
	aom_codec_err_t aom_codec_err_t_s6[1];
	aom_codec_ctx_t aom_codec_ctx_t_p_s4[1];
	unsigned int unsignedint_s4[1];
	unsigned int unsignedint_s1[1];
	aom_image_t *aom_image_t_p_h4[1] = { 0 };
	int int_s1[1];
	unsigned char unsignedchar_p_s0[128];
	int int_s0[1];
	aom_codec_err_t aom_codec_err_t_s2[1];
	aom_codec_err_t aom_codec_err_t_s1[1];
	const char *char_p_cg2[1] = { 0 };
	uint8_t *uint8_t_p_h0[1] = { 0 };
	aom_image_t *aom_image_t_p_h3[1] = { 0 };
	const aom_codec_cx_pkt_t *aom_codec_cx_pkt_t_p_cg0[1] = { 0 };
	memcpy(char_p_s5, data, sizeof(char_p_s5));data += sizeof(char_p_s5);
	char_p_s5[sizeof(char_p_s5) - 1] = 0;
	memcpy(aom_codec_iter_t_p_s0, data, sizeof(aom_codec_iter_t_p_s0));data += sizeof(aom_codec_iter_t_p_s0);
	memcpy(aom_metadata_insert_flags_s0, data, sizeof(aom_metadata_insert_flags_s0));data += sizeof(aom_metadata_insert_flags_s0);
	memcpy(aom_codec_err_t_s7, data, sizeof(aom_codec_err_t_s7));data += sizeof(aom_codec_err_t_s7);
	memcpy(aom_codec_stream_info_t_p_s0, data, sizeof(aom_codec_stream_info_t_p_s0));data += sizeof(aom_codec_stream_info_t_p_s0);
	memcpy(char_p_s3, data, sizeof(char_p_s3));data += sizeof(char_p_s3);
	char_p_s3[sizeof(char_p_s3) - 1] = 0;
	memcpy(long_s0, data, sizeof(long_s0));data += sizeof(long_s0);
	memcpy(aom_codec_err_t_s5, data, sizeof(aom_codec_err_t_s5));data += sizeof(aom_codec_err_t_s5);
	memcpy(aom_codec_err_t_s0, data, sizeof(aom_codec_err_t_s0));data += sizeof(aom_codec_err_t_s0);
	memcpy(unsignedint_s3, data, sizeof(unsignedint_s3));data += sizeof(unsignedint_s3);
	memcpy(aom_codec_err_t_s4, data, sizeof(aom_codec_err_t_s4));data += sizeof(aom_codec_err_t_s4);
	memcpy(char_p_s1, data, sizeof(char_p_s1));data += sizeof(char_p_s1);
	char_p_s1[sizeof(char_p_s1) - 1] = 0;
	memcpy(char_p_s4, data, sizeof(char_p_s4));data += sizeof(char_p_s4);
	char_p_s4[sizeof(char_p_s4) - 1] = 0;
	memcpy(char_p_s6, data, sizeof(char_p_s6));data += sizeof(char_p_s6);
	char_p_s6[sizeof(char_p_s6) - 1] = 0;
	memcpy(aom_codec_err_t_s3, data, sizeof(aom_codec_err_t_s3));data += sizeof(aom_codec_err_t_s3);
	memcpy(unsignedint_s2, data, sizeof(unsignedint_s2));data += sizeof(unsignedint_s2);
	memcpy(char_p_s2, data, sizeof(char_p_s2));data += sizeof(char_p_s2);
	char_p_s2[sizeof(char_p_s2) - 1] = 0;
	memcpy(aom_codec_err_t_s8, data, sizeof(aom_codec_err_t_s8));data += sizeof(aom_codec_err_t_s8);
	memcpy(aom_codec_dec_cfg_t_p_s0, data, sizeof(aom_codec_dec_cfg_t_p_s0));data += sizeof(aom_codec_dec_cfg_t_p_s0);
	memcpy(OBU_TYPE_s0, data, sizeof(OBU_TYPE_s0));data += sizeof(OBU_TYPE_s0);
	memcpy(__uint32_t_s0, data, sizeof(__uint32_t_s0));data += sizeof(__uint32_t_s0);
	memcpy(aom_img_fmt_s0, data, sizeof(aom_img_fmt_s0));data += sizeof(aom_img_fmt_s0);
	memcpy(char_p_s0, data, sizeof(char_p_s0));data += sizeof(char_p_s0);
	char_p_s0[sizeof(char_p_s0) - 1] = 0;
	memcpy(unsignedint_s0, data, sizeof(unsignedint_s0));data += sizeof(unsignedint_s0);
	memcpy(int64_t_s0, data, sizeof(int64_t_s0));data += sizeof(int64_t_s0);
	memcpy(aom_codec_enc_cfg_t_p_s0, data, sizeof(aom_codec_enc_cfg_t_p_s0));data += sizeof(aom_codec_enc_cfg_t_p_s0);
	memcpy(aom_codec_err_t_s6, data, sizeof(aom_codec_err_t_s6));data += sizeof(aom_codec_err_t_s6);
	memcpy(unsignedint_s4, data, sizeof(unsignedint_s4));data += sizeof(unsignedint_s4);
	memcpy(unsignedint_s1, data, sizeof(unsignedint_s1));data += sizeof(unsignedint_s1);
	memcpy(int_s1, data, sizeof(int_s1));data += sizeof(int_s1);
	memcpy(unsignedchar_p_s0, data, sizeof(unsignedchar_p_s0));data += sizeof(unsignedchar_p_s0);
	unsignedchar_p_s0[sizeof(unsignedchar_p_s0) - 1] = 0;
	memcpy(int_s0, data, sizeof(int_s0));data += sizeof(int_s0);
	memcpy(aom_codec_err_t_s2, data, sizeof(aom_codec_err_t_s2));data += sizeof(aom_codec_err_t_s2);
	memcpy(aom_codec_err_t_s1, data, sizeof(aom_codec_err_t_s1));data += sizeof(aom_codec_err_t_s1);
	//dyn array init
	memcpy(unsignedlong_s0, data, sizeof(unsignedlong_s0));data += sizeof(unsignedlong_s0);
	uint8_t_p_h0[0] = (uint8_t*)malloc(unsignedlong_s0[0]);
	memcpy(uint8_t_p_h0[0], data, unsignedlong_s0[0]);
	data += unsignedlong_s0[0];

	char_p_cg0[0] =  aom_obu_type_to_string(OBU_TYPE_s0[0]);
	if (char_p_cg0[0] == 0) goto clean_up;
	aom_codec_iface_t_p_g0[0] =  aom_codec_av1_cx();
	if (aom_codec_iface_t_p_g0[0] == 0) goto clean_up;
	aom_codec_err_t_s0[0] =  aom_codec_enc_init_ver(aom_codec_ctx_t_p_s0, aom_codec_iface_t_p_g0[0], aom_codec_enc_cfg_t_p_s0, long_s0[0], int_s0[0]);
	aom_codec_err_t_s1[0] =  aom_codec_get_stream_info(aom_codec_ctx_t_p_s0, aom_codec_stream_info_t_p_s0);
	aom_codec_err_t_s2[0] =  aom_codec_enc_config_set(aom_codec_ctx_t_p_s0, aom_codec_enc_cfg_t_p_s0);
	aom_codec_err_t_s3[0] =  aom_codec_set_option(aom_codec_ctx_t_p_s0, char_p_s0, char_p_s1);
	aom_codec_err_t_s1[0] =  aom_codec_control(aom_codec_ctx_t_p_s0, int_s0[0], char_p_s2, char_p_s3);
	aom_codec_err_t_s2[0] =  aom_codec_get_stream_info(aom_codec_ctx_t_p_s0, aom_codec_stream_info_t_p_s0);
	aom_codec_cx_pkt_t_p_cg0[0] =  aom_codec_get_cx_data(aom_codec_ctx_t_p_s0, aom_codec_iter_t_p_s0);
	if (aom_codec_cx_pkt_t_p_cg0[0] == 0) goto clean_up;
	aom_codec_err_t_s4[0] =  aom_codec_dec_init_ver(aom_codec_ctx_t_p_s1, aom_codec_iface_t_p_g0[0], aom_codec_dec_cfg_t_p_s0, long_s0[0], int_s0[0]);
	aom_codec_err_t_s0[0] =  aom_codec_dec_init_ver(aom_codec_ctx_t_p_s2, aom_codec_iface_t_p_g0[0], aom_codec_dec_cfg_t_p_s0, long_s0[0], int_s0[0]);
	aom_codec_cx_pkt_t_p_cg1[0] =  aom_codec_get_cx_data(aom_codec_ctx_t_p_s0, aom_codec_iter_t_p_s0);
	if (aom_codec_cx_pkt_t_p_cg1[0] == 0) goto clean_up;
	aom_codec_err_t_s5[0] =  aom_codec_set_option(aom_codec_ctx_t_p_s2, char_p_s1, char_p_s1);
	aom_codec_err_t_s0[0] =  aom_codec_dec_init_ver(aom_codec_ctx_t_p_s3, aom_codec_iface_t_p_g0[0], aom_codec_dec_cfg_t_p_s0, long_s0[0], int_s0[0]);
	aom_image_t_p_g0[0] =  aom_codec_get_frame(aom_codec_ctx_t_p_s1, aom_codec_iter_t_p_s0);
	if (aom_image_t_p_g0[0] == 0) goto clean_up;
	aom_codec_err_t_s5[0] =  aom_codec_set_frame_buffer_functions(aom_codec_ctx_t_p_s1, &f195ae08f, &fbb19e6c8, char_p_s4);
	aom_codec_err_t_s6[0] =  aom_codec_set_frame_buffer_functions(aom_codec_ctx_t_p_s1, &f195ae08f, &fbb19e6c8, char_p_s5);
	aom_image_t_p_g1[0] =  aom_codec_get_frame(aom_codec_ctx_t_p_s0, aom_codec_iter_t_p_s0);
	if (aom_image_t_p_g1[0] == 0) goto clean_up;
	int_s1[0] =  aom_img_add_metadata(aom_image_t_p_g1[0], __uint32_t_s0[0], uint8_t_p_h0[0], unsignedlong_s0[0], aom_metadata_insert_flags_s0[0]);
	aom_image_t_p_h2[0] =  aom_img_alloc_with_border(aom_image_t_p_g0[0], aom_img_fmt_s0[0],  ((uint)unsignedint_s0[0]) % 1024,  ((uint)unsignedint_s1[0]) % 1024,  ((uint)unsignedint_s2[0]) % 1024,  ((uint)unsignedint_s3[0]) % 1024,  ((uint)unsignedint_s4[0]) % 1024);
	if (aom_image_t_p_h2[0] == 0) goto clean_up;
	aom_image_t_p_h3[0] =  aom_img_alloc_with_border(aom_image_t_p_g0[0], aom_img_fmt_s0[0],  ((uint)unsignedint_s2[0]) % 1024,  ((uint)unsignedint_s2[0]) % 1024,  ((uint)unsignedint_s2[0]) % 1024,  ((uint)unsignedint_s2[0]) % 1024,  ((uint)unsignedint_s1[0]) % 1024);
	if (aom_image_t_p_h3[0] == 0) goto clean_up;
	aom_image_t_p_h4[0] =  aom_img_wrap(aom_image_t_p_h2[0], aom_img_fmt_s0[0],  ((uint)unsignedint_s1[0]) % 1024,  ((uint)unsignedint_s4[0]) % 1024,  ((uint)unsignedint_s0[0]) % 1024, unsignedchar_p_s0);
	if (aom_image_t_p_h4[0] == 0) goto clean_up;
	aom_image_t_p_h5[0] =  aom_img_wrap(aom_image_t_p_h2[0], aom_img_fmt_s0[0],  ((uint)unsignedint_s2[0]) % 1024,  ((uint)unsignedint_s4[0]) % 1024,  ((uint)unsignedint_s0[0]) % 1024, unsignedchar_p_s0);
	if (aom_image_t_p_h5[0] == 0) goto clean_up;
	aom_img_flip(aom_image_t_p_g1[0]);
	aom_codec_err_t_s7[0] =  aom_codec_encode(aom_codec_ctx_t_p_s2, aom_image_t_p_h3[0], int64_t_s0[0], unsignedlong_s0[0], long_s0[0]);
	char_p_cg1[0] =  aom_codec_error(aom_codec_ctx_t_p_s0);
	if (char_p_cg1[0] == 0) goto clean_up;
	char_p_cg2[0] =  aom_codec_error(aom_codec_ctx_t_p_s0);
	if (char_p_cg2[0] == 0) goto clean_up;
	aom_codec_err_t_s8[0] =  aom_codec_enc_init_ver(aom_codec_ctx_t_p_s4, aom_codec_iface_t_p_g0[0], aom_codec_enc_cfg_t_p_s0, long_s0[0], int_s1[0]);
	aom_image_t_p_g6[0] =  aom_codec_get_frame(aom_codec_ctx_t_p_s3, aom_codec_iter_t_p_s0);
	if (aom_image_t_p_g6[0] == 0) goto clean_up;
	aom_fixed_buf_t_p_h0[0] =  aom_codec_get_global_headers(aom_codec_ctx_t_p_s4);
	if (aom_fixed_buf_t_p_h0[0] == 0) goto clean_up;
	aom_codec_err_t_s3[0] =  aom_codec_set_frame_buffer_functions(aom_codec_ctx_t_p_s3, &f195ae08f, &fbb19e6c8, char_p_s6);
	aom_codec_err_t_s7[0] =  aom_codec_set_option(aom_codec_ctx_t_p_s1, char_p_s4, char_p_s0);

clean_up:
	aom_codec_destroy(aom_codec_ctx_t_p_s0);
	aom_codec_destroy(aom_codec_ctx_t_p_s3);
	aom_codec_destroy(aom_codec_ctx_t_p_s2);
	if (aom_image_t_p_h2[0] != 0) aom_img_free(aom_image_t_p_h2[0]);
	aom_codec_destroy(aom_codec_ctx_t_p_s1);
	if (aom_fixed_buf_t_p_h0[0] != 0) free(aom_fixed_buf_t_p_h0[0]);
	if (aom_image_t_p_h5[0] != 0) aom_img_free(aom_image_t_p_h5[0]);
	aom_codec_destroy(aom_codec_ctx_t_p_s4);
	if (aom_image_t_p_h4[0] != 0) aom_img_free(aom_image_t_p_h4[0]);
	if (uint8_t_p_h0[0] != 0) free(uint8_t_p_h0[0]);
	if (aom_image_t_p_h3[0] != 0) aom_img_free(aom_image_t_p_h3[0]);

	return 0;
}

int cmpfunc (const void * a, const void * b)
{return ( *(unsigned*)a - *(unsigned*)b );}

// Forward-declare the libFuzzer's mutator callback.
extern "C" size_t LLVMFuzzerMutate(uint8_t *Data, size_t Size, size_t MaxSize);

extern "C" size_t LLVMFuzzerCustomMutator(uint8_t *Data, size_t Size, size_t MaxSize, unsigned int Seed) {

	// select the field to mutate: fized or a dynamic one
	unsigned field = (unsigned)(rand() % (COUNTER_NUMBER + 1));
	// mutate the fixed part
	if (field == 0) {
		uint8_t fixed_field[FIXED_SIZE];
		memcpy(fixed_field, Data, FIXED_SIZE);
		size_t new_fixed_data = LLVMFuzzerMutate(fixed_field, FIXED_SIZE, FIXED_SIZE);

		if (new_fixed_data > FIXED_SIZE) {
			printf("[ERROR] for the fixed size, I have a longer size");
			exit(1);
		}
		// LLVMFuzzerMutate could reduce the seed size
		if (new_fixed_data < FIXED_SIZE) {
			size_t to_append_size = FIXED_SIZE-new_fixed_data;
			for (unsigned i = 0; i < to_append_size; i++)
			// fixed_field[new_fixed_data+i] = (uint8_t)rand();
			fixed_field[new_fixed_data+i] = 0x0;
		}
		memcpy(Data, fixed_field, FIXED_SIZE);
		return Size;
	// mutate one of the dynamic fields
	} else {
		unsigned dyn_field_idx = field - 1;

		size_t counter = 0;
		uint8_t *counter_addr = Data + FIXED_SIZE;
		uint8_t *buffer_start, *buffer_end;
		size_t to_read = MIN(sizeof(size_t), counter_size[0]);
		memcpy(&counter, counter_addr, to_read);
		buffer_start = Data + FIXED_SIZE + counter_size[0];
		buffer_end = buffer_start + counter;
		if (dyn_field_idx != 0) {
			for (unsigned i = 1; i < COUNTER_NUMBER && i != (dyn_field_idx + 1); i++) {
				to_read = MIN(sizeof(size_t), counter_size[i]);
				memcpy(&counter, buffer_end, to_read);
				counter_addr = buffer_end;
				buffer_start = buffer_end + counter_size[i];
				buffer_end = buffer_start + counter;

			}
		}
		uint8_t dynamic_field[NEW_DATA_LEN];

		memcpy(dynamic_field, buffer_start, counter);

		size_t new_dynamic_data = LLVMFuzzerMutate(dynamic_field, counter, NEW_DATA_LEN);

		if (new_dynamic_data > NEW_DATA_LEN) {
			printf("[ERROR] for the dynamic size, I have a longer size");
			exit(1);
		}

		size_t new_whole_data_size = Size - (counter - new_dynamic_data);
		if (new_whole_data_size == 0 || new_whole_data_size > MaxSize)
			return 0;

		uint8_t *new_data = (uint8_t*)malloc(new_whole_data_size);
		uint8_t *new_data_original = new_data;
		memset(new_data, 0, new_whole_data_size);

		// copy what stays before the old dyn buffer
		memcpy(new_data, Data, counter_addr - Data);
		new_data += counter_addr - Data;

		// store the new counter
		size_t real_counter_size = MIN(sizeof(size_t), counter_size[dyn_field_idx]);
		memcpy(new_data, &new_dynamic_data, real_counter_size);
		new_data += counter_size[dyn_field_idx];

		// store the new dynamic field
		memcpy(new_data, dynamic_field, new_dynamic_data);
		new_data += new_dynamic_data;

		// dynamic region is not the last one
		if (buffer_end != Data + Size && new_dynamic_data > 0) {
			size_t leftover_size = (Data + Size) - buffer_end;
			memcpy(new_data, buffer_end, leftover_size);
		}

		// re-transfer the new seed into the Data buffer
		memcpy(Data, new_data_original, new_whole_data_size);
		free(new_data_original);

		return new_whole_data_size;
	}
}
