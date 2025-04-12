#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>
#include "library.h"

void set_default(my_struct* s) {
   s->field_a = 4;
   s->field_b = 8;
   s->field_c = 'X';
   s->field_d = 12.3;
}

void swap_fields(int* x1, int* x2) {
   int temp = *x1;
   *x1 = *x2;
   *x2 = temp;
}

my_struct* api1(int a, int b, char c, double d, short f) {
   my_struct* s = (my_struct*)malloc(sizeof(my_struct));

   if (f) {
      set_default(s);
   } /* else {
      s->field_a = a;
      s->field_b = b;
      s->field_c = c;
      s->field_d = d;
   } */

   return s;
}

void api2(my_struct* s) {

   if (s->field_d > 0.5) {
      swap_fields(&s->field_a, &s->field_b);
   } else {
      s->field_c = 'q';
   }
}
