#include <stdio.h>
#include <stdlib.h>

int main(int argc, char** argv) {

    int *dd[1][1] = { 0 };

    printf("doing something\n");

    free(dd[0]);

    return 0;
}