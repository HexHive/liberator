#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

#include "libxml/xmlschemas.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  static bool initialized = false;
  if (!initialized) {
    xmlInitParser();
    initialized = true;
  }

  xmlSchemaValidCtxtPtr context = xmlSchemaNewValidCtxt(nullptr);
  if (context == nullptr) {
    return 0;
  }

  xmlSAXHandlerPtr handler;
  void* user_data;
  xmlSchemaSAXPlug(context, &handler, &user_data);
  xmlSchemaFreeValidCtxt(context);
  return 0;
}

