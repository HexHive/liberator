// #include <uriparser/UriDefsConfig.h>
// #include <uriparser/UriBase.h>
// #include <uriparser/UriDefsAnsi.h>
// #include <uriparser/UriDefsUnicode.h>
// #include <uriparser/UriIp4.h>
#include <uriparser/Uri.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdint.h>

int main(int argc, char** argv) {

    int s0 = 0xA;
    int s1 = 0xB;

    UriMemoryManager UriMemoryManager_p_s0;	
	uriEmulateCalloc(&UriMemoryManager_p_s0, s0, s1);

	return 0;
}