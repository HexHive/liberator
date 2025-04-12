
#include <stdlib.h>
#include <inttypes.h>

typedef struct a_struct my_struct;
typedef struct sub_struct1 my_sub_struct1;
typedef struct sub_struct2 my_sub_struct2;

my_struct* create(int a, int b, char* file_path);
void first(my_struct *s, int a);
void second(my_struct *s, int b);
void close(my_struct *s);
void third(void* b, my_struct *s);
void foo(int a);
void indirect_test(my_struct *s, int a);