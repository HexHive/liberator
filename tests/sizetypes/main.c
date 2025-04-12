#include <ctype.h>
#include <stdio.h>

int main(int argc, char** argv) {

    wchar_t wchar_t_p_s1[128];
    wchar_t wchar_x;
    printf("sizeof(wchar_t): %zu\n", sizeof(wchar_x));
    printf("sizeof(wchar_t[128]): %zu\n", sizeof(wchar_t_p_s1));

    return 0;
}