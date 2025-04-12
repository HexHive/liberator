
#include <stdlib.h>
#include <inttypes.h>

// struct a_struct {
//  int field_a;
// 	int field_b;
// 	char* generic_data; // malloc(len_data)
// };

extern "C" {

typedef struct a_struct my_struct;

my_struct* create(char*);
void close(my_struct *);
void my_free(void*);
void* my_malloc(size_t);

}