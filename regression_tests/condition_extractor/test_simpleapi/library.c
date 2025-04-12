#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>

#include "library.h"

struct a_struct {
    int field_a;
	int field_b;
	void* generic_data; // cast to sub_struct1* or sub_struct2*
};

struct sub_struct1 {
	int field_sa;
};

struct sub_struct2 {
	double field_sb;
};

void bar1() {
	// return 1;
}

void bar2() {
	// return 1;
}

void do_casting(my_struct* s, short flag) {
	
	if (flag) {
		my_sub_struct1 *ss = (my_sub_struct1*) s->generic_data;
		ss->field_sa = 10;
	} else {
		my_sub_struct2 *ss = (my_sub_struct2*) s->generic_data;
		ss->field_sb = 5.2;
	}
}


// void foo(int a) {
// 	int x = 0;
// 	if (a > 0)
// 		// x = 10;
// 		bar1();
// 	else
// 		// x = 11;
// 		bar1();
// 	return;
// }

void modify(my_struct* s, int n_struct) {
	for (int i = 0; i < n_struct; i++) {
		s[i].field_a = i;
	}
}

void needs_array(my_struct* s, int n_struct) {

	modify(s, n_struct);
	// for (int i = 0; i < 10; i++) {
	// 	s[i].field_a = i;
	// }
	// int i = 10;
	// int a = 0;
	// while (a < n_struct) { 
	// 	s[a].field_a = i;
	// }

	// do {
	// 	s[a].field_a = i;
	// } while (a < n_struct);

	// while(1) {
	// 	if (a >= n_struct)
	// 		break;
		
	// 	if (a > i)
	// 		break;
	// 	s[a].field_a = i;

	// 	if (a >= n_struct2)
	// 		break;
	// }

}

void needs_array_1(my_struct** s, int n_struct) {

	// for (int i = 0; i < n_struct; i++) {
	// 	s[i]->field_a = i;
	// }

	modify(s, n_struct);

}

void my_free(int xx, my_struct* s) {
	free(s);
}

void* my_malloc(size_t s) {
	if (s == 0)
		return NULL;

	return malloc(s);
}

// void indirect_test(my_struct *s, int a) {

// 	void (*fun_ptr)(my_struct*,int) = NULL;
// 	if (a > 0)
// 		fun_ptr = &first;
// 	else 
// 		fun_ptr = &second;

// 	fun_ptr(s, a);

// 	s->field_a = 10;
// 	s->field_b = 11;

// 	my_free(s);
// }

my_struct* create(int a, int b, char* file_path) {
	my_struct *s = my_malloc(sizeof(my_struct));

	if (s == NULL) {
		return NULL;
	}

	if (a == 0) {
		my_free(0, s);
		return 0;
	}

	s->field_a = a;
	s->field_b = b;

	open(file_path, "r");
	
	my_struct *s1 = my_malloc(sizeof(my_struct));

	// int xx[10];
	// for (int i = 0; i < 10; i++) {
	// 	if (i > 5)
	// 		xx[i] = i + 1;
	// 	else 
	// 		xx[i] = i * 2;
	// }

	return s;
}

// void first(my_struct *s, int a) {
// 	s->field_b = a;
// 	if (s->field_c < 0)
// 		s->field_c = -s->field_c;
// }

// void second(my_struct *s, int b) {
// 	if (s->field_a > 10)
// 		s->field_d = b;
// }

// void third(void* b, my_struct *s) {
// 	s->field_a = (int)b;
// }

// void close(my_struct *s) {
// 	if (s != NULL)
// 		my_free(s);
// }