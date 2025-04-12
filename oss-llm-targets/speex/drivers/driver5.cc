#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <vector>

#include "ogg/ogg.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);

  ogg_stream_state os;
  ogg_stream_init(&os, stream.ConsumeIntegral<long>());

  ogg_packet op;
  ogg_packet_clear(&op);

  while (stream.remaining_bytes() > 0) {
    auto bytes = stream.ConsumeBytes<uint8_t>(stream.ConsumeIntegralInRange<size_t>(0, stream.remaining_bytes()));
    ogg_stream_packetin(&os, &op);
    ogg_page og;
    ogg_stream_pageout(&os, &og);
  }

  ogg_stream_clear(&os);
  ogg_packet_clear(&op);
  
  return 0;
}

