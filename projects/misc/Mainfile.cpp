#include<stdio.h>
#include<iostream>
#include<time.h>

#include "test_struct_size.h"
using namespace std;


#define MX_TCASE (10000000000000)
#define MX_NUMBER (100000)

void comp_by_bit_manipulation() {
    FILE* fd = fopen("output.txt", "w");
    int tcase = rand() % MX_TCASE;
    while (tcase--) {
        int sign = rand() % 2; 
        int a = sign ? rand() % MX_NUMBER : -1 * (rand() % MX_NUMBER);
        bool by_shift = false;
        bool by_comp = false;
        if (a & 1 << 31)  by_shift = true;
        if (a < 0) by_comp = true;
        int check = 0;
        if (by_shift == by_comp) check = 1;
        fprintf(fd, "%10d : %02d : %02d : %02d\n", a, by_shift, by_comp, check);
    }
    fclose(fd);
}




int main() {
    srand(time(NULL));
    comp_by_bit_manipulation();

    init_test_struct_size();
    return EXIT_SUCCESS;
}