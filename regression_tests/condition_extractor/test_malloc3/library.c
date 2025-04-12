#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>

#include "library.h"

#define PTHREADPOOL_CACHELINE_SIZE 64

extern "C" {

struct_t* pthreadpool_allocate(
	size_t threads_count)
{
	assert(threads_count >= 1);

	const size_t threadpool_size = sizeof(struct_t) + threads_count;
	struct_t* threadpool = NULL;
	
  if (posix_memalign((void**) &threadpool, PTHREADPOOL_CACHELINE_SIZE, threadpool_size) != 0) {
    return NULL;
  }

	memset(threadpool, 0, threadpool_size);
	return threadpool;
}

}