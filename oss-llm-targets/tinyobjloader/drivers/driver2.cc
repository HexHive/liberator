#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>

#include "tiny_obj_loader.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider provider(data, size);
  int attrib = provider.ConsumeIntegral<int>();
  std::unique_ptr<tinyobj::attrib_t> attrib_ptr(
      reinterpret_cast<tinyobj::attrib_t*>(attrib));
  std::vector<tinyobj::shape_t> shapes;
  std::vector<tinyobj::material_t> materials;
  std::string warn;
  std::string err;
  const char* filename =
      provider.ConsumeRandomLengthString().c_str();
  const char* mtl_basedir =
      provider.ConsumeRandomLengthString().c_str();
  const bool triangulate = provider.ConsumeBool();
  const bool default_vcols_fallback = provider.ConsumeBool();

  tinyobj::LoadObj(attrib_ptr.get(), &shapes, &materials, &warn, &err,
                   const_cast<char*>(filename), const_cast<char*>(mtl_basedir),
                   triangulate, default_vcols_fallback);

  return 0;
}

