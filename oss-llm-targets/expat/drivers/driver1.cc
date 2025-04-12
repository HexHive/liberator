#include <fuzzer/FuzzedDataProvider.h>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>
#include "expat.h"
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider provider(data, size);
  // Create a new parser
  XML_Parser parser = XML_ParserCreate(nullptr);
  if (parser == nullptr) {
    return 0;
  }
  // Create a new external entity parser
  XML_Parser external_parser = XML_ExternalEntityParserCreate(
      parser, provider.PickValueInArray<const char*>(
                  {nullptr, "context", "context2", "context3", "context4"}),
      provider.PickValueInArray<const char*>(
          {nullptr, "encodingName", "encodingName2", "encodingName3",
           "encodingName4"}));
  if (external_parser == nullptr) {
    XML_ParserFree(parser);
    return 0;
  }
  XML_ParserFree(external_parser);
  XML_ParserFree(parser);
  return 0;
}
