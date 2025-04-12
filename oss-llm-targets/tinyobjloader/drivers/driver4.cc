#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <string>

#include "tiny_obj_loader.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider provider(data, size);
  const std::string filename = provider.ConsumeRemainingBytesAsString();
  tinyobj::attrib_t attrib;
  std::vector<tinyobj::shape_t> shapes;
  std::vector<tinyobj::material_t> materials;

  std::string warn;
  std::string err;

  tinyobj::LoadObj(&attrib, &shapes, &materials, &warn, &err, filename.c_str(),
                   nullptr);

  return 0;
}


