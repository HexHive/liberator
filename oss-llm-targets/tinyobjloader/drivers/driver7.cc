#include <fuzzer/FuzzedDataProvider.h>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>
#include "tiny_obj_loader.h"
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  tinyobj::ObjReaderConfig config;
  config.mtl_search_path = ".";
  config.triangulate = true;
  config.vertex_color = true;
  std::string filename = stream.ConsumeRemainingBytesAsString();
  tinyobj::ObjReader reader;
  reader.ParseFromFile(filename, config);
  return 0;
}
