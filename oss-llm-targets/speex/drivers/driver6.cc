#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

#include "ogg/ogg.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider provider(data, size);
  ogg_stream_state os;
  ogg_page og;
  ogg_stream_init(&os, provider.ConsumeIntegral<int>());
  ogg_stream_pagein(&os, &og);
  ogg_stream_clear(&os);
  ogg_stream_pageout_fill(&os, &og, provider.ConsumeIntegral<int>());
  return 0;
}


