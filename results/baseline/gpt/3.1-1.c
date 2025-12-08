#include <stdio.h>

void readLine(char *buffer, size_t size) {
    if (fgets(buffer, size, stdin) != NULL) {
        // Remove the newline character if present
        size_t len = strlen(buffer);
        if (len > 0 && buffer[len - 1] == '\n') {
            buffer[len - 1] = '\0';
        }
    }
}
