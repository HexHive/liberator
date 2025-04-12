// SHA2 test program
#include "md5.h"
#include <iostream> // for std::cout only, not needed for hashing library
#include <fstream>

int main(int argc, char** argv)
{
    if (argc != 2) {
        std::cout << "No file given" << std::endl;
        return 1;
    }

    MD5 md5stream;

    std::ifstream dump_file;
    dump_file.open(argv[1]);

    //get length of file
    dump_file.seekg(0, std::ios::end);
    size_t length = dump_file.tellg();
    dump_file.seekg(0, std::ios::beg);

    char *buffer = (char*) malloc(length);

    //read file
    dump_file.read(buffer, length);
    md5stream.add(buffer, length);

    free(buffer);
    buffer = NULL;
    
    dump_file.close();
    std::cout << md5stream.getHash() << std::endl;

    return 0;
}