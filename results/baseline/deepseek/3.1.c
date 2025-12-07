#include <stdio.h>

void read_line(char *buffer, int size) {
    fgets(buffer, size, stdin);
}
