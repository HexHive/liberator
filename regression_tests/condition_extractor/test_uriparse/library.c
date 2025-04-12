#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>

#include "library.h"

int loop_indirect(const char *first, const char *afterLast) {

	const char * walk = first;
	// const char * walk = walk1;
	// const char * keyFirst = first;
	// const char * keyAfter = NULL;
	// const char * valueFirst = NULL;
	// const char * valueAfter = NULL;
	// URI_TYPE(QueryList) ** prevNext = dest;
	// int nullCounter;
	// int * itemsAppended = (itemCount == NULL) ? &nullCounter : itemCount;

	// if ((dest == NULL) || (first == NULL) || (afterLast == NULL)) {
	// 	return URI_ERROR_NULL;
	// }

	// if (first > afterLast) {
	// 	return URI_ERROR_RANGE_INVALID;
	// }

	int x = 0;

	// URI_CHECK_MEMORY_MANAGER(memory);  /* may return */
	/* Parse query string */
	for (; walk < afterLast; walk++) {
		switch (*walk) {
			case 'A':
			default:
				x++;
		}
	}


	return 0;
}