#include "ucl.h"
#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>
#ifdef __cplusplus
extern "C" {
#endif

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const std::string key = stream.ConsumeRemainingBytesAsString();
  ucl_object_t* top = ucl_object_new();
  ucl_object_t* elt = ucl_object_new();
  ucl_object_replace_key(top, elt, const_cast<char*>(key.c_str()), key.size(), true);
  ucl_object_unref(elt);
  ucl_object_unref(top);
  return 0;
}

#ifdef __cplusplus
}
#endif
