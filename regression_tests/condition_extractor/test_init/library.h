
#include <stdlib.h>
#include <inttypes.h>

// struct a_struct {
//  int field_a;
// 	int field_b;
// 	char* generic_data; // malloc(len_data)
// };

extern "C" {


// must remaining incomplete
struct a_iface {
	int field_a = 0;
	const char *field_ptr = "halo!";
};

// complete but not fuzzing friendly
struct a_context {
	int field_x;
	long field_y;
	a_iface* m_iface;
};



typedef struct a_iface iface_t;
typedef struct a_context a_context_t;


iface_t* get_a_struct();
void init_a_context(iface_t*, a_context_t*, int, short);
int fake_init(iface_t*, a_context_t*);
int use_context( a_context_t*, int);
int get_something(iface_t*, int);

}