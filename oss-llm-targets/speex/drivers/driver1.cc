#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>

#include "ogg/ogg.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  static bool initialized = false;
  ogg_sync_state sync;
  if (!initialized) {
    ogg_sync_init(&sync);
    initialized = true;
  }

  FuzzedDataProvider stream(data, size);
  ogg_packet op;
  ogg_stream_state os;
  ogg_stream_init(&os, stream.ConsumeIntegral<long>());
  size_t consumed = stream.ConsumeData(&op, sizeof(op));
  if (consumed != sizeof(op)) {
    return 0;
  }
  ogg_stream_packetin(&os, &op);
  ogg_stream_clear(&os);
  return 0;
}

