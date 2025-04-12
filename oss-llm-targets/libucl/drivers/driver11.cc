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
  FuzzedDataProvider provider(data, size);

  ucl_object_t *top = ucl_object_new_full(UCL_OBJECT, 0);
  ucl_object_t *elt = ucl_object_new_full(UCL_OBJECT, 0);
  std::string key = provider.ConsumeRemainingBytesAsString();
  size_t keylen = key.size();
  bool copy_key = provider.ConsumeBool();

  ucl_object_replace_key(top, elt, const_cast<char*>(key.c_str()), keylen, copy_key);

  ucl_object_unref(top);
  ucl_object_unref(elt);

  return 0;
}

#ifdef __cplusplus
}
#endif
