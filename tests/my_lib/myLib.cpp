#include "myLib.hpp"
#include <iostream>
#include <string.h>

using namespace std;

#define INIT 0
#define START 1
#define STOP 2

int STATE = INIT;

typedef struct {
    int x;
    int z;
    char s[10];
} my_connection;


void echo_connection(my_connection a_conn, my_connection *r_conn) {
    cout << "ciao\n";
}

my_connection make_connection(int arg_x, int arg_z, char *arg_s) {
    my_connection a_ret;
    a_ret.x = arg_x;
    a_ret.z = arg_z;

    strncpy(a_ret.s, arg_s, strlen(a_ret.s));

    return a_ret;
}

static my_connection a_conn;

my_connection* make_connection2(int arg_x, int arg_z, char *arg_s) {
    a_conn.x = arg_x;
    a_conn.z = arg_z;

    strncpy(a_conn.s, arg_s, strlen(a_conn.s));

    return &a_conn;
}

void print_value( int *x, int b )
{
    cout << *x << "\n";
    *x = b;
}

void set_state(int x) {
    STATE=x;
}

int get_state() {
    return STATE;
}

void leak() {
    my_connection a = make_connection(0xA, 0xB, "ciao");
}

int taint() {
    // leak();
    return 10;
}

void startservice() {
    if (get_state() == START)
        return;

    set_state(START);

    int x = taint();
}

void stopservice() {
    if (get_state() == START)
        return;

    set_state(INIT);
}

int getservicestate() {
    return get_state();
}



// int foo() {
//     int a = 10;
//     int b = a + 3;

//     if (a > 3)
//         b = a * 2;
//     else
//         b = a - 4;

//     return b;
// }
