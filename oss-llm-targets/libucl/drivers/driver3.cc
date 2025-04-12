#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>

#include "ucl.h"
#ifdef __cplusplus
extern "C" {
#endif

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider stream(data, size);
  const std::string comments_string = stream.ConsumeRemainingBytesAsString();
  const std::string obj_string = stream.ConsumeRemainingBytesAsString();
  const std::string comment_string = stream.ConsumeRemainingBytesAsString();
  ucl_object_t* comments = ucl_object_new();
  ucl_object_t* obj = ucl_object_new();
  ucl_object_t* comment = ucl_object_new();
  ucl_comments_add(comments, obj, const_cast<char*>(comment_string.c_str()));
  ucl_object_free(comments);
  ucl_object_free(obj);
  ucl_object_free(comment);
  return 0;
}

#ifdef __cplusplus
}
#endif
