#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>

#include <libxml/xmlschemastypes.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  FuzzedDataProvider provider(data, size);

  xmlSchemaValidCtxtPtr ctxt = xmlSchemaNewValidCtxt(nullptr);
  if (ctxt == nullptr) {
    return 0;
  }

  const std::string filename = provider.ConsumeRemainingBytesAsString();

  xmlSchemaValidateFile(ctxt, filename.c_str(), 0);
  xmlSchemaFreeValidCtxt(ctxt);

  return 0;
}

