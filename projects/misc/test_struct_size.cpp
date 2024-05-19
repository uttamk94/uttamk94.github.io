#include "test_struct_size.h"
#include <stdio.h>


void init_test_struct_size() {

    one_byte_t one_bye_s;
    byte_and_short_t byte_and_short;
    int_and_byte_t int_and_bytes;
    
    printf("one_byte size: %d\n", sizeof(one_bye_s));
    printf("byte and short size: %d\n", sizeof(byte_and_short));
    printf("byte and short size: %d\n", sizeof(int_and_bytes));
}