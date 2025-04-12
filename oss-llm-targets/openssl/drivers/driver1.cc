#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include "punycode.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const std::string encoded = stream.ConsumeRemainingBytesAsString();
  const char* encoded_ptr = encoded.c_str();
  const size_t encoded_length = encoded.length();
  const size_t decoded_length = 1024;
  unsigned int decoded[decoded_length];
  unsigned int decoded_length_ptr = decoded_length;
  ossl_punycode_decode(encoded_ptr, encoded_length, decoded, &decoded_length_ptr);
  return 0;
}
