
#include <fcntl.h> /* open() O_RDONLY */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

#define O_BINARY 0 /* So it does nothing in Linux/Unix */

/*
 * Libdwarf library callers can only use these headers.
 */
#ifdef __cplusplus
extern "C" {
#endif
#include "dwarf.h"
#include "libdwarf.h"

/*  This now initializes local variables to zero
    rather than leaving them uninitialized.
    When uninitialized consistent behavior is
    unlikely, run-to-run.  And
    crashes are likely.
    David Anderson 30 May 2023.
*/
/*
 * A fuzzer that simulates a small part of the simplereader.c example.
 */
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  char filename[256];
  sprintf(filename, "/tmp/libfuzzer.%d", getpid());

  FILE *fp = fopen(filename, "wb");
  if (!fp) {
    return 0;
  }
  fwrite(data, size, 1, fp);
  fclose(fp);

  Dwarf_Debug dbg = 0;
  int res = DW_DLV_ERROR;
  Dwarf_Error error = 0;
  Dwarf_Handler errhand = 0;
  Dwarf_Ptr errarg = 0;
  int regtabrulecount = 0;
  int curopt = 0;

  int fd = open(filename, O_RDONLY | O_BINARY);
  if (fd < 0) {
    exit(EXIT_FAILURE);
  }

  res = dwarf_init_b(fd, DW_GROUPNUMBER_ANY, errhand, errarg, &dbg, &error);

  if (res != DW_DLV_OK) {
    dwarf_dealloc_error(dbg, error);
  } else {
    Dwarf_Unsigned dw_index = 0;
    Dwarf_Die die = 0;
    Dwarf_Unsigned dw_index_count = 0;
    res = dwarf_debug_addr_index_to_addr(die, dw_index, &dw_index_count, &error);
    if (res != DW_DLV_OK) {
      dwarf_dealloc_error(dbg, error);
      dwarf_finish(dbg);
      close(fd);
      unlink(filename);
      return 0;
    }
  }

  dwarf_finish(dbg);
  close(fd);
  unlink(filename);
  return 0;
}

#ifdef __cplusplus
}
#endif
