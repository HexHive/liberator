#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include "plist/plist.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const std::string plist_string = stream.ConsumeRemainingBytesAsString();
  plist_t root_node = nullptr;
  plist_from_xml(plist_string.c_str(), plist_string.size(), &root_node);
  plist_print(root_node);
  plist_free(root_node);

  return 0;
}
