#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include <libxml/xmlreader.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const std::string xml_document = stream.ConsumeRemainingBytesAsString();
  xmlTextReaderPtr reader = xmlReaderForMemory(xml_document.c_str(), size, nullptr,
                                               nullptr, 0);
  if (reader == nullptr) {
    return 0;
  }
  xmlTextReaderRead(reader);
  xmlTextReaderSchemaValidate(reader, nullptr);
  xmlFreeTextReader(reader);
  return 0;
}


