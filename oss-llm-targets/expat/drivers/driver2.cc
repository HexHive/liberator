#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include "expat.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const std::string xml_string = stream.ConsumeRemainingBytesAsString();
  XML_Parser xml_parser = XML_ParserCreateNS(nullptr, ' ');
  XML_Parse(xml_parser, xml_string.c_str(), xml_string.size(), true);
  XML_ParserFree(xml_parser);
  return 0;
}


