#include <stdint.h>
#include <cstddef>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <cstdlib>
#include <time.h>

/* MIN_SEED_SIZE = 128 (FIXED SIZE) +
                     8 (COUNTER 1) +
                     4 (COUNTER 2)
                ----------------
                   140
*/
#define FIXED_SIZE 128
#define MIN_SEED_SIZE 140
#define COUNTER_NUMBER 2
const unsigned counter_size[COUNTER_NUMBER] = { 8, 4 };

#define NEW_DATA_LEN 4096

// int cmpfunc (const void * a, const void * b) {
//    return ( *(unsigned*)a - *(unsigned*)b );
// }

// // Forward-declare the libFuzzer's mutator callback.
// extern "C" size_t LLVMFuzzerMutate(uint8_t *Data, size_t Size, size_t MaxSize);

// extern "C" size_t LLVMFuzzerCustomMutator(uint8_t *Data, size_t Size,
//                                           size_t MaxSize, unsigned int Seed) {

//     // printf("LLVMFuzzerCustomMutator\n");
//     size_t counter_size_sum = 0;
//     for (int i = 0; i < COUNTER_NUMBER; i++)
//         counter_size_sum += counter_size[i];

//     if (Size < FIXED_SIZE || 
//         Size >= (NEW_DATA_LEN-counter_size_sum))
//         return 0;

//     // printf("check 1 done\n");

//     unsigned cut[COUNTER_NUMBER] = { 0 };

//     uint8_t NewData[NEW_DATA_LEN];
//     size_t NewDataSize = sizeof(NewData);

//     uint8_t *NewDataPtr = NewData;
//     uint8_t *DataPtr = Data;

//     size_t NewDataLen = LLVMFuzzerMutate(Data, Size, NEW_DATA_LEN);
//     // printf("LLVMFuzzerMutate\n");

//     if (NewDataLen < FIXED_SIZE || NewDataLen >= (NEW_DATA_LEN-counter_size_sum))
//         return 0;

//     // printf("check 2 done\n");

//     // printf("=== BEGIN ===\n");

//     size_t DynamicPart = NewDataLen - FIXED_SIZE;
//     // if (NewDataLen == NEW_DATA_LEN)
//     // printf("DynamicPart %zu\n", DynamicPart);
//     // for (int i = 0; i < COUNTER_NUMBER; i++)
//     //     DynamicPart -= counter_size[i];
//     // printf("after DynamicPart %zu\n", DynamicPart);
//     // if (DynamicPart <= 0)
//     //     DynamicPart = 0;

//     // printf("DynamicPart = %u\n", DynamicPart);
//     // find cuts
//     cut[0] = 0;
//     if (DynamicPart == 0) {
//         for (int i = 1; i < COUNTER_NUMBER; i++)
//             cut[i] = 0;
//     }
//     else {
//         for (int i = 1; i < COUNTER_NUMBER; i++)
//             cut[i] = rand() % DynamicPart;
//         qsort(cut, COUNTER_NUMBER, sizeof(unsigned), cmpfunc);
//     }

//     // printf("DynamicPart = %zu\n", DynamicPart);

//     // printf("NewDataPtr LAST: %p\n", NewDataPtr + sizeof(NewData));

//     // printf("DataPtr 0: %p\n", DataPtr);
//     // printf("NewDataPtr 0: %p\n", NewDataPtr);

//     // copy Fixed Part
//     unsigned long slice_len = FIXED_SIZE;
//     memcpy(NewDataPtr, DataPtr, slice_len);
//     DataPtr += slice_len;
//     NewDataPtr += slice_len;

//     // printf("DataPtr F: %p\n", DataPtr);
//     // printf("NewDataPtr F: %p\n", NewDataPtr);

//     unsigned long NewDataFinalLen = slice_len;
    
//     // printf("MaxDataLen = %d\n", NEW_DATA_LEN);
//     // printf("FixPart = %d\n", FIXED_SIZE);
//     for (int i = 0; i < COUNTER_NUMBER; i++) {
//         if (i == COUNTER_NUMBER - 1) {
//             // printf("COUNTER_NUMBER - 1\n");
//             slice_len = DynamicPart - cut[i];
//         }
//         else {
//             // printf("normal\n");
//             slice_len = cut[i+1] - cut[i];
//         }
//         memcpy(NewDataPtr, &slice_len, counter_size[i]);
//         NewDataPtr += counter_size[i];
//         // printf("slice_len %zu\n", slice_len);
//         memcpy(NewDataPtr, DataPtr, slice_len);
//         DataPtr += slice_len;
//         NewDataPtr += slice_len;

//         NewDataFinalLen += slice_len + counter_size[i];

//         // printf("DataPtr i: %p\n", DataPtr);
//         // printf("NewDataPtr i: %p\n", NewDataPtr);
//     }


//     memcpy(Data, NewData, NewDataFinalLen);

//     return NewDataFinalLen;
// }

// // I need some randomness
// extern "C" int LLVMFuzzerInitialize(int *argc, char ***argv) {
//     srand(time(0));
//     return 0;
// }

char x[10];

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {

    // printf("begin driver\n");

    // if (size < MIN_SEED_SIZE) {
    //     // printf("eary exit\n");
    //     return 0;
    // }

    if (size == 4) {
        if (data[0] == 'H' &&
            data[1] == 'H' &&
            data[2] == 'H' &&
            data[3] == 'H')
            x[-1] = 0x10;
    }

    // printf("passed min size\n");
  
    // char char_p_s4[128];
    // size_t size_t_s1[1];
	// char *char_p_s0 = "gxkpoprtbtdkbgkndysk.bin";
	// int int_s0[1];	
	// char *char_p_h2[128] = { 0 };
	
	// memcpy(char_p_s4, data, sizeof(char_p_s4));data += sizeof(char_p_s4);

	// //file init
	// memcpy(size_t_s1, data, sizeof(size_t_s1));data += sizeof(size_t_s1);
    // // size_t_s1[0] = size_t_s1[0] % 100;
	// FILE *p0 = fopen(char_p_s0, "w");
	// fwrite(data, size_t_s1[0], 1, p0);
	// fclose(p0);data += size_t_s1[0];

    // // if (size_t_s1[0] != 0) {
    // //     printf("wrote file %zu\n", size_t_s1[0]);
    // // }

	// //dyn array init
	// memcpy(int_s0, data, sizeof(int_s0));data += sizeof(int_s0);
    // // int_s0[0] = abs(int_s0[0]) % 100;
	// char_p_h2[0] = (char*)malloc(int_s0[0]);
	// memcpy(char_p_h2[0], data, int_s0[0]);
	// data += int_s0[0];

    // // if (int_s0[0] != 0) {
    // //     printf("wrote array %d\n", int_s0[0]);
    // // }

    // // printf("end driver\n");

    // // if (size_t_s1[0] != 0 && int_s0[0] != 0)
    // //     abort();


// clean_up:
// 	if (char_p_h2[0] != 0) free(char_p_h2[0]);

    return 0;
}