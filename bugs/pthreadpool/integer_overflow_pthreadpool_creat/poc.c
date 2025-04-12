#include <pthreadpool.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>

int main() {
	pthreadpool_create(0xb800000000000000);
	return 0;
}
