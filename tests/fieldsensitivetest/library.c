#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>
#include "library.h"

void swap_fields(my_struct *m) {
   int t = m->field_a;
   m->field_a = m->field_b;
   m->field_b = t;
}

void my_api(my_struct *m) {
     if (m->field_a == 0) {
       swap_fields(m);
   }
}
