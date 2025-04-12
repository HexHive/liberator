#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstdio>

#include "ogg/ogg.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  ogg_stream_state os;
  ogg_packet op;

  ogg_stream_init(&os, 0);

  FuzzedDataProvider provider(data, size);
  while (provider.remaining_bytes() > 0) {
    int ret = ogg_stream_packetin(&os, &op);
    if (ret != 0) {
      goto end;
    }
    const size_t next_size = provider.ConsumeIntegralInRange<size_t>(
        0,
        provider.remaining_bytes());
    auto next_input = provider.ConsumeBytes<uint8_t>(next_size);
    op.packet = next_input.data();
    op.bytes = next_input.size();
    op.b_o_s = 0;
    op.e_o_s = 0;
    op.granulepos = 0;
    op.packetno = 0;
  }

  end:
  ogg_stream_clear(&os);
  return 0;
}
