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


int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  char filename[] = "/tmp/fuzz-libdwfl.XXXXXX";
  int fd;
  ssize_t n;

  fd = mkstemp(filename);
  assert(fd >= 0);

  n = write_retry(fd, data, size);
  assert(n == (ssize_t) size);

  close(fd);

  Dwarf_Addr base = 0;
  Dwarf_Addr start = 0;
  Dwarf_Addr end = 0;
  Dwarf_Op *expr = NULL;
  size_t exprlen = 0;

  Dwfl *dwfl = dwfl_begin(&cb);
  dwfl_report_begin(dwfl);

  Dwfl_Module *mod = dwfl_report_offline(dwfl, filename, filename, -1);
  dwfl_module_getdwarf(mod, &base);
  Dwarf_Attribute *attr = NULL;
  ptrdiff_t offset = dwarf_getlocations(attr, offset, &base, &start, &end, &expr, &exprlen);

  dwfl_end (dwfl);
  unlink(filename);
  return 0;
}

