#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>

#include "library.h"

extern "C" {

struct a_struct {
	int field_a;
	int field_b;
	int len_data;
	char* generic_data; // malloc(len_data)
};

void my_free(void* s) {
	free(s);
}

void* my_malloc(size_t s) {
	if (s == 0)
		return NULL;

	return malloc(s);
}

my_struct* create(char* file_path) {
	my_struct *s = (my_struct*) my_malloc(sizeof(my_struct));

	if (s == NULL) {
		return NULL;
	}

	FILE *fp = fopen(file_path, "r");
	
	s->field_a = getw(fp);
	s->field_b = getw(fp);

	unsigned int len_data = getw(fp);
	s->len_data = len_data;
	s->generic_data = (char*) malloc(len_data);
	fread(s->generic_data, len_data, 1, fp);	

	fclose(fp);

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

void set_a(my_struct *s, int a) {
	s->field_a = a;
}

void set_b(my_struct *s, int b) {
	s->field_b = b;
}

void set_data(my_struct *s, char *b, size_t len_b)  {
	if (s->generic_data != NULL)
		free(s->generic_data);
	s->generic_data = (char*) malloc(len_b);
	memcpy(s->generic_data, b, len_b);
}

int get_a(my_struct *s) {
	return s->field_a;
}

int get_b(my_struct *s) {
	return s->field_b;
}

void get_data(my_struct *s, char *b) {
	memcpy(b, s->generic_data, s->len_data);
}

void operation(my_struct *s) {
	if (s->field_a > s->field_b) {
		int i = 0;
		for (;i < s->len_data; i++)
			if (i % 2 == 0)
				s->generic_data[i] = s->field_a * i;
			else
				s->generic_data[i] = s->field_b * i;
	}
}

}
