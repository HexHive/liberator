#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <string>

#include "ucl.h"
#ifdef __cplusplus
extern "C" {
#endif

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const uint8_t slate_width = stream.ConsumeIntegral<uint8_t>();
  const uint8_t slate_height = stream.ConsumeIntegral<uint8_t>();
  ucl_object_t *slate_image = ucl_object_new();
  if (slate_image == nullptr) {
    return 0;
  }
  const char *x_position = stream.ConsumeRemainingBytesAsString().c_str();
  const char *y_position = stream.ConsumeRemainingBytesAsString().c_str();
  ucl_object_t *text_color = ucl_object_new();
  if (text_color == nullptr) {
    return 0;
  }
  ucl_object_t *font_ptr = ucl_object_new();
  if (font_ptr == nullptr) {
    return 0;
  }
  const std::string text = stream.ConsumeRemainingBytesAsString();

  ucl_object_compare(slate_image, font_ptr);
  ucl_object_unref(slate_image);
  ucl_object_unref(text_color);
  ucl_object_unref(font_ptr);
  return 0;
}

#ifdef __cplusplus
}
#endif
