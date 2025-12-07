#include <stdio.h>

void readLine(char *buffer, int bufferSize) {
    if (fgets(buffer, bufferSize, stdin) != NULL) {
        char *newline = strchr(buffer, '\n');
        if (newline) {
            *newline = '\0';
        }
    }
}
