#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>

#include "library.h"

extern "C" {

iface_t global_a_struct;

iface_t* get_a_struct() {
	return &global_a_struct;
}
void init_a_context(iface_t *a, a_context_t *ctx, int x, short flag) {

	if (flag == 0)
		return;

	ctx->m_iface = a;
	ctx->field_x = x;
}

int use_context( a_context_t *ctx, int x) {
	if (ctx == nullptr) 
		return 0;

	if (ctx->m_iface->field_a == 0)
		return 0;

	return ctx->field_x == x;
}

int fake_init(iface_t *i, a_context_t *ctx) {
	return ctx->m_iface->field_a == 1; 
}

int get_something(iface_t *a, int x) {
	return a->field_a;
}

}