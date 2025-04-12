#include <unistd.h>
#include "ucl.h"
#ifdef __cplusplus
extern "C" {
#endif

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
	struct ucl_parser *parser;
	parser = ucl_parser_new(0);

	int fd = 0;
	int priority = 0;

	ucl_parser_add_fd_priority(parser, fd, priority);

	if (ucl_parser_get_error(parser) != NULL) {
		return 0;
	}

	ucl_parser_free (parser);
        return 0;
}

#ifdef __cplusplus
}
#endif
