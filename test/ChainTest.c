#include <stdio.h>

int mockme(int one, int two, int three)
{
    printf("mockme(%d, %d, %d)\n", one, two, three);
    return one;
}

int
callme(int one, int two, int three)
{
    return mockme(one, two, three);
}
