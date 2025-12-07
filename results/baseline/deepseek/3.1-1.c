#include <stdio.h>
#include <string.h>

void read_line(char *buffer, int size) {
    if (fgets(buffer, size, stdin) != NULL) {
        // Remove the newline character if present
        buffer[strcspn(buffer, "\n")] = '\0';
    }
}
