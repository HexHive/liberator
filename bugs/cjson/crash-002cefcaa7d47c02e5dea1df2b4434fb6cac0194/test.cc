#include <cjson/cJSON.h>

#include <stdlib.h>
#include <stdint.h>

// issue at https://github.com/DaveGamble/cJSON/issues/880

int main(int argc, char** argv) {

        cJSON *o = cJSON_CreateArray();
        cJSON *a = cJSON_CreateArray();
        cJSON *b = cJSON_CreateArray();

        cJSON_AddItemToArray(o, a);
        cJSON_AddItemToArray(a, b);
        cJSON_AddItemToArray(b, o);

        cJSON *x = cJSON_Duplicate(o, 1);

        cJSON_Delete(o);
        cJSON_Delete(a);
        cJSON_Delete(b);
        cJSON_Delete(x);

        return 0;
}

/*
commit: 3249730

line 2773:
/* Walk the ->next chain for the child. *./
    child = item->child;
    while (child != NULL)
    {
        newchild = cJSON_Duplicate(child, true); /* Duplicate (with recurse) each item in the ->next chain *./
        if (!newchild)
        {
            goto fail;
        }

*/