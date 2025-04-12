
#include <stdlib.h>
#include <inttypes.h>


extern "C" {


struct a_struct {
 int field_a;
	int field_b;
	char* generic_data; // malloc(len_data)
};

typedef a_struct struct_t;

struct_t* pthreadpool_allocate(size_t threads_count);

}