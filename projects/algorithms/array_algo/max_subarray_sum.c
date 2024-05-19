#include <stdio.h>
#include<time.h>
#include<stdlib.h>

int max_subarray_sum(int *ary, int length) {
    int max_so_far = 0, max_ending_here = 0;

    for (int i = 0; i < length; i++) {
        max_ending_here += *(ary + i); 
        if (max_ending_here < 0) max_ending_here = 0;
        if (max_so_far < max_ending_here) max_so_far = max_ending_here;
    }
    return max_so_far;
}

int max_subarray_sum_se_index(int *ary, int length, int *start, int *end) {
    int max_so_far = 0, max_ending_here = 0;
    int s = 0;
    *start = *end = 0;
    
    for (int i = 0; i < length; i++) {
        max_ending_here += *(ary + i); 
        if (max_ending_here < 0) {
            max_ending_here = 0;
            s = i+1;
        }
        if (max_so_far < max_ending_here) {
            max_so_far = max_ending_here;
            *end = i;
            *start = s;
        }
    }
    return max_so_far;
}

void print_array(int *ary, int length) {
    for (int i = 0; i < length; i++) printf("%d ", *(ary + i));
    printf("\n");
}

void print_array_se_index(int *ary, int s, int e) {
    for (int i = s; i <= e; i++) printf("%d ", *(ary + i));
    printf("\n");
}

int main() {
    srand(time(NULL));
    int ary[10];
    for (int i = 0; i < 10; i++) { ary[i] = (rand() % 20) & 1 ? (-1 * rand() % 10) : rand() % 10;}
    
    print_array(ary, 10);

    printf("max: %d\n", max_subarray_sum(ary, 10));

    int start=0, end=0;
    int mxx = max_subarray_sum_se_index(ary, 10, &start, &end);
    printf("maxx: %d, start: %d, end: %d\n", mxx, start, end);
    print_array_se_index(ary, start, end);


    return 0;
}