#include <stdio.h>
#include <string.h>
#include "network_lib.hpp"

int main ( void )
{
    connection a_conn;

    unsigned char ip[4] = {192, 168, 0, 1};
    unsigned int port = 8080;

    connect(ip, port, &a_conn);

    char *msg_out = "I am a message";
    // size_t msg_out_len = strlen(msg_out);

    if (send_msg(msg_out, sizeof(msg_out), a_conn) < 0) {
        printf("not sent, error");
        return 1;
    }

    char msg_in[20];
    if (receive_msg(msg_in, sizeof(msg_in), a_conn) < 0) {
        printf("not received, error");
        return 1;
    }

    close(&a_conn);

    return 0;
}
