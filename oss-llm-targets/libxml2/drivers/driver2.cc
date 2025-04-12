#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

#include "libxml/xmlschemastypes.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider provider(data, size);
  const size_t filename_size = provider.ConsumeIntegralInRange<size_t>(0, size);
  const std::string filename = provider.ConsumeBytesAsString(filename_size);
  const int options = provider.ConsumeIntegral<int>();
  const xmlSchemaValidCtxtPtr ctxt = xmlSchemaNewValidCtxt(nullptr);
  if (ctxt == nullptr) {
    return 0;
  }
  const int ret = xmlSchemaValidateFile(ctxt, filename.c_str(), options);
  xmlSchemaFreeValidCtxt(ctxt);
  return 0;
}

