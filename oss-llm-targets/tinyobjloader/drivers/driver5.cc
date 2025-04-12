#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>
#include <vector>

#include "tiny_obj_loader.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  tinyobj::ObjReader* obj_reader = new tinyobj::ObjReader();
  tinyobj::ObjReaderConfig* obj_reader_config =
      new tinyobj::ObjReaderConfig();
  obj_reader_config->mtl_search_path = stream.ConsumeRemainingBytesAsString();
  std::vector<uint8_t> bytes =
      stream.ConsumeRemainingBytes<uint8_t>();
  std::string obj_string(bytes.begin(), bytes.end());
  std::string mtl_string = stream.ConsumeRemainingBytesAsString();
  obj_reader->ParseFromString(obj_string, mtl_string);
  obj_reader->ParseFromFile(obj_string, *obj_reader_config);
  delete obj_reader;
  delete obj_reader_config;
  return 0;
}

