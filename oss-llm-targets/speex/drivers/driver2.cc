#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

#include "fuzzer/FuzzedDataProvider.h"
#include "ogg/ogg.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  ogg_stream_state os;
  ogg_page og;
  ogg_packet op;

  ogg_stream_init(&os, -1);

  FuzzedDataProvider provider(data, size);
  while (provider.remaining_bytes() > 0) {
    // The maximum size of the packet is 65535 bytes.
    const size_t next_size = provider.ConsumeIntegralInRange<size_t>(
        0,
        provider.remaining_bytes());
    auto next_input = provider.ConsumeBytes<uint8_t>(next_size);

    ogg_stream_packetin(&os, &op);
    op.packet = next_input.data();
    op.bytes = next_input.size();
    op.b_o_s = 0;
    op.e_o_s = 0;
    op.granulepos = 0;
    op.packetno = 0;
  }

  ogg_stream_clear(&os);

  return 0;
}

