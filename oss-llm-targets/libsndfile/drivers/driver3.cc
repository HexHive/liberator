#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include "sndfile.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const uint8_t num_channels = stream.ConsumeIntegral<uint8_t>();
  const uint8_t format_type = stream.ConsumeIntegral<uint8_t>();
  const SF_INFO info = {
      .channels = num_channels,
      .format = format_type,
  };
  sf_format_check(&info);
  return 0;
}
