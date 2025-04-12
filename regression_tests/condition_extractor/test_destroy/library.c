#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>

#include "library.h"

extern "C" {

// iface_t global_a_struct;

// iface_t* get_a_struct() {
// 	return &global_a_struct;
// }
// void init_a_context(iface_t *a, a_context_t *ctx, int x, short flag) {

// 	if (flag == 0)
// 		return;

// 	ctx->m_iface = a;
// 	ctx->field_x = x;
// }

// int use_context( a_context_t *ctx, int x) {
// 	if (ctx == nullptr) 
// 		return 0;

// 	if (ctx->m_iface->field_a == 0)
// 		return 0;

// 	return ctx->field_x == x;
// }

// int fake_init(iface_t *i, a_context_t *ctx) {
// 	return ctx->m_iface->field_a == 1; 
// }

// int get_something(iface_t *a, int x) {
// 	return a->field_a;
// }

// int vpx_codec_destroy(vpx_codec_ctx_t *ctx) {
//   int res;

//   if (!ctx)
//     res = 0;
//   else if (!ctx->iface || !ctx->priv)
//     res = 1;
//   else {
//     // ctx->iface->destroy((vpx_codec_alg_priv_t *)ctx->priv);

// 	  memset(ctx, 0, 16);
//     // ctx->iface = NULL;
//     // ctx->name = NULL;
//     // ctx->priv = NULL;
//     res = 2;
//   }

//   return res;
// }

int vpx_rb_read_bit(struct vpx_read_bit_buffer *rb, unsigned int data_sz) {

  if (data_sz > 100)
    return 1;

  const size_t off = rb->bit_offset;
  const size_t p = off >> 3;
  const int q = 7 - (int)(off & 0x7);
  if (rb->bit_buffer + p < rb->bit_buffer_end) {
    const int bit = (rb->bit_buffer[p] >> q) & 1;
    rb->bit_offset = off + 1;
    return bit;
  } else {
    return 0;
  }
}

int (*read_bit)(struct vpx_read_bit_buffer *rb, unsigned int data_sz) = &vpx_rb_read_bit;

int decoder_peek_si_internal(const uint8_t *data, unsigned int data_sz) {
    struct vpx_read_bit_buffer rb = { data, data + data_sz, 0};
    return read_bit(&rb, data_sz);
}

}