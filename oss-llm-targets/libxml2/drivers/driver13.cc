#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include "libxml/parser.h"
#include "libxml/relaxng.h"
#include "libxml/xmlreader.h"
#include "libxml/xmlschemastypes.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  xmlTextReaderPtr reader = xmlReaderForMemory(
      reinterpret_cast<const char*>(data), size, nullptr, nullptr, 0);
  if (reader == nullptr) {
    return 0;
  }

  xmlSchemaParserCtxtPtr schema_parser_context =
      xmlSchemaNewParserCtxt(nullptr);
  if (schema_parser_context == nullptr) {
    xmlFreeTextReader(reader);
    return 0;
  }

  xmlSchemaPtr schema = xmlSchemaParse(schema_parser_context);
  if (schema == nullptr) {
    xmlSchemaFreeParserCtxt(schema_parser_context);
    xmlFreeTextReader(reader);
    return 0;
  }

  xmlTextReaderSetSchema(reader, schema);

  xmlFreeTextReader(reader);
  xmlSchemaFreeParserCtxt(schema_parser_context);
  xmlSchemaFree(schema);

  return 0;
}
