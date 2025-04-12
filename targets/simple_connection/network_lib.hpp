#include <stddef.h>

#ifndef LIB1_H_INCLUDED
#define LIB1_H_INCLUDED

#ifdef __cplusplus
   extern "C" {
#endif

struct connection {
   unsigned char ip[4];
   unsigned int port;
   bool is_connected;
};

void connect(unsigned char ip[4], unsigned int port, connection *conn);
unsigned int send_msg(char* buff, size_t buff_len, connection conn);
unsigned int receive_msg(char* buff, size_t buff_len, connection conn);
void close(connection *conn);

#ifdef __cplusplus
   }
#endif

#endif /* LIB1_H_INCLUDED */
