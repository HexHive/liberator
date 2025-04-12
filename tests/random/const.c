#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>

int main(int argc, char** argv) {

    char *char_p_s0 = "gskuieebotwnkjueoilb.bin";
    uint64_t uint64_t_s1[1];
    size_t size_t_s0[1];
    int int_s0[1];
    int int_s2[1];
    int int_s1[1];
    char char_p_s1[128];
    uint32_t uint32_t_s0[1];
    uint64_t uint64_t_s0[1];
    // TIFFTagMethods *TIFFTagMethods_p_h0[1] = { 0 };
    uint16_t uint16_t_s0[1];
    // TIFF *TIFF_p_h0[1] = { 0 };

    // FIX PART
    // memcpy(uint64_t_s1, data, sizeof(uint64_t_s1));data += sizeof(uint64_t_s1);
    // memcpy(int_s0, data, sizeof(int_s0));data += sizeof(int_s0);
    // memcpy(int_s2, data, sizeof(int_s2));data += sizeof(int_s2);
    // memcpy(int_s1, data, sizeof(int_s1));data += sizeof(int_s1);
    // memcpy(char_p_s1, data, sizeof(char_p_s1));data += sizeof(char_p_s1);
    // char_p_s1[sizeof(char_p_s1) - 1] = 0;
    // memcpy(uint32_t_s0, data, sizeof(uint32_t_s0));data += sizeof(uint32_t_s0);
    // memcpy(uint64_t_s0, data, sizeof(uint64_t_s0));data += sizeof(uint64_t_s0);
    // memcpy(uint16_t_s0, data, sizeof(uint16_t_s0));data += sizeof(uint16_t_s0);
    unsigned long tot_fix = 0;
    tot_fix += sizeof(uint64_t_s1);printf("tot_fix = %zu\n", tot_fix);
    tot_fix += sizeof(int_s0);printf("tot_fix = %zu\n", tot_fix);
    tot_fix += sizeof(int_s2);printf("tot_fix = %zu\n", tot_fix);
    tot_fix += sizeof(int_s1);printf("tot_fix = %zu\n", tot_fix);
    tot_fix += sizeof(char_p_s1);printf("tot_fix = %zu\n", tot_fix);
    tot_fix += sizeof(uint32_t_s0);printf("tot_fix = %zu\n", tot_fix);
    tot_fix += sizeof(uint64_t_s0);printf("tot_fix = %zu\n", tot_fix);
    tot_fix += sizeof(uint16_t_s0);printf("tot_fix = %zu\n", tot_fix);


    // DYNAMIC PART
    // memcpy(size_t_s0, data, sizeof(size_t_s0));data += sizeof(size_t_s0);
    // printf("slice_len [in driver] = %zu\n", size_t_s0[0]);
    // FILE *p0 = fopen(char_p_s0, "w");
    // fwrite(data, size_t_s0[0], 1, p0);
    // fclose(p0);data += size_t_s0[0];

    return 0;
}