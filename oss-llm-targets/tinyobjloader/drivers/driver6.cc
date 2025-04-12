#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include "tiny_obj_loader.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider provider(data, size);
  auto obj_string = provider.ConsumeRandomLengthString();
  std::string tinyobj_obj_string = obj_string;
  tinyobj::ObjReaderConfig config = tinyobj::ObjReaderConfig();
  tinyobj::ObjReader reader = tinyobj::ObjReader();
  reader.ParseFromFile(tinyobj_obj_string, config);
  return 0;
}


