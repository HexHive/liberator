#include <plist/plist.h>
#include <stdio.h>

extern "C" int LLVMFuzzerTestOneInput(const unsigned char* data, size_t size)
{
	plist_t root_node = NULL;
	plist_from_bin(reinterpret_cast<const char*>(data), size, &root_node);
	plist_print(root_node);
	plist_free(root_node);

	return 0;
}
