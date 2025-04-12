#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>

#include "library.h"

extern "C" {

typedef struct internal_hooks
{
    void* (*allocate)(size_t size);
    void (*deallocate)(void *pointer);
    void* (*reallocate)(void *pointer, size_t size);
} internal_hooks;

#define internal_malloc malloc
#define internal_free free
#define internal_realloc realloc

static internal_hooks global_hooks = { malloc, internal_free, internal_realloc };
static internal_hooks *hooks = &global_hooks;

struct a_struct {
	int field_a;
	int field_b;
	int len_data;
	char* generic_data; // malloc(len_data)
};

void my_free(void* s) {
	hooks->deallocate(s);
}

void* my_malloc(size_t s) {
	if (s == 0)
		return NULL;

	return hooks->allocate(s);
	// return malloc(s);
}

my_struct* create(char* file_path) {
	my_struct *s = (my_struct*) my_malloc(sizeof(my_struct));
	// my_struct *s = (my_struct*) hooks->allocate(sizeof(my_struct));

	// if (s == NULL) {
	// 	return NULL;
	// }

	// FILE *fp = fopen(file_path, "r");
	
	// s->field_a = getw(fp);
	// s->field_b = getw(fp);

	// unsigned int len_data = getw(fp);
	// s->len_data = len_data;
	// s->generic_data = (char*) my_malloc(len_data);
	// fread(s->generic_data, len_data, 1, fp);	

	// fclose(fp);

	return s;
}

void close(my_struct *s) {

	if (s == NULL)
		return;

	my_free(s->generic_data);
	s->generic_data = NULL;
	my_free(s);
	// s = NULL;
}

}
