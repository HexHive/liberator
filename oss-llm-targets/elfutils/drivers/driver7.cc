#include <assert.h>
#include <fcntl.h>
#include <gelf.h>
#include <inttypes.h>
#include <libelf.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include "libdwfl.h"
#include "system.h"

static const char *debuginfo_path = "";
static const Dwfl_Callbacks cb  = {
  NULL,
  dwfl_standard_find_debuginfo,
  NULL,
  (char **)&debuginfo_path,
};

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  char filename[] = "/tmp/fuzz-libdwfl.XXXXXX";
  int fd;
  ssize_t n;

  fd = mkstemp(filename);
  assert(fd >= 0);

  n = write_retry(fd, data, size);
  assert(n == (ssize_t) size);

  close(fd);

  Dwfl *dwfl = dwfl_begin(&cb);
  dwfl_report_begin(dwfl);

  Dwfl_Module *mod = dwfl_report_offline(dwfl, filename, filename, -1);

  Dwfl_Frame *frame = NULL;
  Dwfl_Line *line = NULL;
  Dwarf_Addr pc;
  bool isactivation;

  dwfl_frame_pc(frame, &pc, &isactivation);

  dwfl_end (dwfl);
  unlink(filename);
  return 0;
}
