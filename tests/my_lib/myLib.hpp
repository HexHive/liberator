#ifndef LIB1_H_INCLUDED
#define LIB1_H_INCLUDED

#ifdef __cplusplus
   extern "C" {
#endif

void print_value ( int x );
int foo();

void startservice();
void stopservice();
int getservicestate();
int taint();
void leak();

#ifdef __cplusplus
   }
#endif

#endif /* LIB1_H_INCLUDED */
