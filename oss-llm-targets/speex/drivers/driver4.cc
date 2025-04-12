#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <memory>

#include "ogg/ogg.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider provider(data, size);
  auto os = std::make_unique<ogg_stream_state>();
  ogg_stream_init(os.get(), provider.ConsumeIntegral<uint32_t>());
  auto op = std::make_unique<ogg_packet>();
  ogg_stream_packetin(os.get(), op.get());
  ogg_stream_packetout(os.get(), op.get());
  ogg_stream_clear(os.get());
  return 0;
}

