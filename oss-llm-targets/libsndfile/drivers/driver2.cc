#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>
#include <vector>

#include "sndfile.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const int command = stream.ConsumeIntegral<int>();
  std::vector<uint8_t> buffer = stream.ConsumeBytes<uint8_t>(stream.remaining_bytes());
  void* pointer = buffer.data();
  const int datasize = stream.remaining_bytes();

  int err = sf_command(nullptr, command, pointer, datasize);

  return err;
}


