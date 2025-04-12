#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include "libxml/parser.h"
#include "libxml/xmlschemas.h"
#include "libxml/xmlreader.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const std::string xml_content = stream.ConsumeRemainingBytesAsString();
  const std::string xsd_content = stream.ConsumeRemainingBytesAsString();
  xmlTextReaderPtr reader = xmlReaderForMemory(xml_content.c_str(),
                                                xml_content.size(), nullptr,
                                                nullptr, 0);
  if (reader == nullptr) {
    return 0;
  }

  xmlSchemaParserCtxtPtr parser_context =
      xmlSchemaNewMemParserCtxt(xsd_content.c_str(), xsd_content.size());
  if (parser_context == nullptr) {
    xmlFreeTextReader(reader);
    return 0;
  }

  xmlSchemaPtr schema = xmlSchemaParse(parser_context);
  if (schema == nullptr) {
    xmlSchemaFreeParserCtxt(parser_context);
    xmlFreeTextReader(reader);
    return 0;
  }

  xmlTextReaderSetSchema(reader, schema);

  xmlSchemaFree(schema);
  xmlSchemaFreeParserCtxt(parser_context);
  xmlFreeTextReader(reader);
  return 0;
}

