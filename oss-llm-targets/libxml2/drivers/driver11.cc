#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

#include "libxml/parser.h"
#include "libxml/xmlreader.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  xmlInitParser();
  xmlTextReaderPtr reader = xmlReaderForMemory((const char*)data, size, nullptr, nullptr, 0);
  if (reader == nullptr) {
    xmlCleanupParser();
    return 0;
  }
  xmlSchemaParserCtxtPtr schema_parser = xmlSchemaNewParserCtxt((const char*)reader);
  if (schema_parser == nullptr) {
    xmlFreeTextReader(reader);
    xmlCleanupParser();
    return 0;
  }
  xmlSchemaPtr schema = xmlSchemaParse(schema_parser);
  if (schema == nullptr) {
    xmlSchemaFreeParserCtxt(schema_parser);
    xmlFreeTextReader(reader);
    xmlCleanupParser();
    return 0;
  }

  int ret = xmlTextReaderSetSchema(reader, schema);
  if (ret == 0) {
    xmlSchemaFree(schema);
    xmlSchemaFreeParserCtxt(schema_parser);
    xmlFreeTextReader(reader);
    xmlCleanupParser();
    return 0;
  }

  xmlSchemaFreeParserCtxt(schema_parser);
  xmlSchemaFree(schema);
  xmlFreeTextReader(reader);
  xmlCleanupParser();
  return 0;
}


