#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include "ucl.h"
#ifdef __cplusplus
extern "C" {
#endif

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const std::string key = stream.ConsumeRemainingBytesAsString();
  ucl_object_t *top = ucl_object_typed_new(UCL_OBJECT);
  ucl_object_replace_key(top, top, (char *)key.c_str(), key.length(), false);
  ucl_object_unref(top);
  return 0;
}

#ifdef __cplusplus
}
#endif
