#include <stdio.h>
#include <stdlib.h>

#define MAX_LENGTH 1024

int read_line(char* buffer) {
    fgets(buffer, MAX_LENGTH, stdin);
    if (buffer[strlen(buffer) - 1] == '\n') {
        buffer[strlen(buffer) - 1] = '\0';
    }
    return strlen(buffer);
}
