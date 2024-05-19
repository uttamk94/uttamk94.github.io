#ifndef TEST_STRUCT_SIZE_H
#define TEST_STRUCT_SIZE_H

typedef struct oneB {
    char ch;
} one_byte_t;

typedef struct bytes{
    char ch;
    short sh;
} byte_and_short_t;

typedef struct five_bytes{
    char ch;
    int integer;
} int_and_byte_t;

void init_test_struct_size();
#endif