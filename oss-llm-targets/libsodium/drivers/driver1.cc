#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider provider(data, size);
  const std::string filename = provider.ConsumeRemainingBytesAsString();
  FILE* fp = fopen(filename.c_str(), "r");
  if (!fp) {
    perror("fopen");
    return 1;
  }
  fclose(fp);
  return 0;
}

void ge25519_from_hash(unsigned char s[32], const unsigned char h[64]) {
  // TODO: Implement this function.
}
