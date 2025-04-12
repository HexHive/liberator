
#include <stdlib.h>
#include <inttypes.h>

// struct a_struct {
//  int field_a;
// 	int field_b;
// 	char* generic_data; // malloc(len_data)
// };

extern "C" {


// // must remaining incomplete
// struct a_iface {
// 	int field_a = 0;
// 	const char *field_ptr = "halo!";
// };

// // complete but not fuzzing friendly
// struct a_context {
// 	int field_x;
// 	long field_y;
// 	a_iface* m_iface;
// };

// typedef struct vpx_codec_ctx {
//   const char *name;             /**< Printable interface name */
//   void *iface;     /**< Interface pointers */
// //   vpx_codec_err_t err;          /**< Last returned error */
//   const char *err_detail;       /**< Detailed info, if available */
//   int init_flags; /**< Flags passed at init time */
// //   union {
// //     /**< Decoder Configuration Pointer */
// //     const struct vpx_codec_dec_cfg *dec;
// //     /**< Encoder Configuration Pointer */
// //     const struct vpx_codec_enc_cfg *enc;
// //     const void *raw;
// //   } config;               /**< Configuration pointer aliasing union */
//   void *priv; /**< Algorithm private storage */
// } vpx_codec_ctx_t;

struct vpx_read_bit_buffer {
  const uint8_t *bit_buffer;
  const uint8_t *bit_buffer_end;
  size_t bit_offset;

//   void *error_handler_data;
//   vpx_rb_error_handler error_handler;
};

// typedef struct a_iface iface_t;
// typedef struct a_context a_context_t;

// iface_t* get_a_struct();
// void init_a_context(iface_t*, a_context_t*, int, short);
// int fake_init(iface_t*, a_context_t*);
// int use_context( a_context_t*, int);
// int get_something(iface_t*, int);
// int vpx_codec_destroy(vpx_codec_ctx_t *ctx);
int decoder_peek_si_internal(const uint8_t *data, unsigned int data_sz);



// int main(int arch, char** argc) {
//   const uint8_t data[1000] = { 0 };
//   unsigned int data_sz = 10;
//   return decoder_peek_si_internal(data, data_sz);
// }

}