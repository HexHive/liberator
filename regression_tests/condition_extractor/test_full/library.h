
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
void set_a(my_struct*,int);
void set_b(my_struct*,int);
void set_data(my_struct *s, char *b, size_t len_b);
int get_a(my_struct*);
int get_b(my_struct*);
void get_data(my_struct*,char*);
void operation(my_struct*);
void close(my_struct *);
void my_free(void*);
void* my_malloc(size_t);

}