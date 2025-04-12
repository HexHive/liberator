#include <fuzzer/FuzzedDataProvider.h>

#include <plist/plist.h>
#include <stdio.h>

extern "C" int LLVMFuzzerTestOneInput(const unsigned char* data, size_t size) {
  FuzzedDataProvider provider(data, size);

  plist_t target = plist_new_dict();
  plist_t source = plist_new_dict();

  plist_dict_merge(&target, source);

  plist_free(target);
  plist_free(source);
  return 0;
}

