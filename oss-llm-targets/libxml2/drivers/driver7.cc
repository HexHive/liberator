#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include <libxml/xmlreader.h>
#include <libxml/xmlschemas.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const char* schema = stream.ConsumeRemainingBytesAsString().c_str();
  xmlParserInputBufferPtr input = xmlParserInputBufferCreateMem(schema, (int) strlen(schema), XML_CHAR_ENCODING_UTF8);
  xmlTextReaderPtr reader = xmlNewTextReader(input, NULL);
  if (reader == nullptr) {
    return 0;
  }
  xmlTextReaderSchemaValidate(reader, schema);
  xmlFreeTextReader(reader);
  xmlFreeParserInputBuffer(input);
  return 0;
}

