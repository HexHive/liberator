#include <pthreadpool.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>

void f1597a0c5 (void *, size_t, size_t, size_t, size_t, size_t, size_t) {
}



int main() {
	pthreadpool_compute_3d_tiled(pthreadpool_create(0), &f1597a0c5, NULL, 0,0,0,0,0,0);
	return 0;
}
