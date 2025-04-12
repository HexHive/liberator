#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include "libxml/parser.h"
#include "libxml/xmlreader.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider provider(data, size);

  // Create an xml reader.
  const std::string xml_input = provider.ConsumeRemainingBytesAsString();
  xmlTextReaderPtr reader = xmlReaderForMemory(xml_input.c_str(),
                                               static_cast<int>(xml_input.size()),
                                               nullptr, nullptr, 0);
  if (reader == nullptr) {
    return 0;
  }

  // Create a schema validator.
  xmlSchemaParserCtxtPtr schema_parser = xmlSchemaNewParserCtxt(
      "http://www.w3.org/2001/XMLSchema");
  if (schema_parser == nullptr) {
    xmlFreeTextReader(reader);
    return 0;
  }

  xmlSchemaPtr schema = xmlSchemaParse(schema_parser);
  if (schema == nullptr) {
    xmlSchemaFreeParserCtxt(schema_parser);
    xmlFreeTextReader(reader);
    return 0;
  }

  xmlSchemaFreeParserCtxt(schema_parser);

  xmlSchemaValidCtxtPtr schema_validator = xmlSchemaNewValidCtxt(schema);
  if (schema_validator == nullptr) {
    xmlFreeTextReader(reader);
    return 0;
  }

  int result = xmlTextReaderSchemaValidateCtxt(reader, schema_validator, 0);

  xmlFreeTextReader(reader);
  xmlSchemaFreeValidCtxt(schema_validator);

  return 0;
}


