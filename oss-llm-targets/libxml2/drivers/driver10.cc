#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include "libxml/globals.h"
#include "libxml/parser.h"
#include "libxml/relaxng.h"
#include "libxml/tree.h"
#include "libxml/xmlreader.h"
#include "libxml/xmlschemas.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  xmlInitParser();
  LIBXML_TEST_VERSION;
  xmlTextReaderPtr reader = xmlReaderForMemory(
      reinterpret_cast<const char*>(data), size, nullptr, nullptr, 0);
  if (reader == nullptr) {
    return 0;
  }

  // We are going to use a default schema validation context.
  xmlSchemaValidCtxtPtr ctxt = xmlSchemaNewValidCtxt(nullptr);
  if (ctxt == nullptr) {
    xmlFreeTextReader(reader);
    return 0;
  }

  // We are going to use the default schema validation options.
  int options = 0;

  // We are going to use the default schema validation options.
  int ret = xmlTextReaderSchemaValidateCtxt(reader, ctxt, options);
  xmlFreeTextReader(reader);
  xmlSchemaFreeValidCtxt(ctxt);
  xmlCleanupParser();
  return 0;
}

