#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>
#include <vector>

#include "tiny_obj_loader.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider provider(data, size);
  tinyobj::attrib_t attrib;
  std::vector<tinyobj::shape_t> shapes;
  std::vector<tinyobj::material_t> materials;
  std::string warning;
  std::string error;
  const std::string filename = provider.ConsumeRemainingBytesAsString();
  tinyobj::LoadObj(&attrib, &shapes, &materials, &warning, &error,
                   const_cast<char*>(filename.c_str()), nullptr, true, true);
  return 0;
}

