#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>
#include <vector>

#include "libxml/xmlschemastypes.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const char* filename = stream.ConsumeBool()
                             ? stream.ConsumeRandomLengthString().c_str()
                             : nullptr;
  int options = stream.ConsumeBool()
                    ? atoi(stream.ConsumeRandomLengthString().c_str())
                    : 0;
  xmlSchemaValidCtxtPtr ctxt = stream.ConsumeBool()
                                   ? xmlSchemaNewValidCtxt(nullptr)
                                   : nullptr;
  int result = xmlSchemaValidateFile(ctxt, filename, options);
  return 0;
}

