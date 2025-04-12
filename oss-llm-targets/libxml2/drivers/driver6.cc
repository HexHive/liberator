#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include "libxml/xmlreader.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const std::string xml = stream.ConsumeRemainingBytesAsString();
  xmlTextReaderPtr reader = xmlReaderForMemory(xml.c_str(), xml.size(), nullptr,
                                               nullptr, 0);
  if (reader == nullptr) {
    return 0;
  }
  const std::string xsd = stream.ConsumeRemainingBytesAsString();
  xmlTextReaderSchemaValidate(reader, xsd.c_str());
  xmlFreeTextReader(reader);
  return 0;
}

