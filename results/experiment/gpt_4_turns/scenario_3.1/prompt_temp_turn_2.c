#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINES 10
#define BUFFER_SIZE 1024

void readLine(char *buffer, size_t size) {
    if (fgets(buffer, size, stdin) == NULL) {
        fprintf(stderr, "Error reading input.\n");
        exit(EXIT_FAILURE);
    }

    // Remove the potential newline character
    size_t len = 0;
    while (buffer[len] != '\0' && buffer[len] != '\n') {
        len++;
    }
    if (buffer[len] == '\n') {
        buffer[len] = '\0';
    }

    printf("Length of the entered line: %zu\n", len);
}

int main() {
    char buffers[MAX_LINES][BUFFER_SIZE];
    size_t current_line = 0;

    printf("Enter up to %d lines of text (each up to %d characters; blank line to finish):\n", MAX_LINES, BUFFER_SIZE - 1);

    while (current_line < MAX_LINES) {
        printf("Line %zu: ", current_line + 1);
        readLine(buffers[current_line], BUFFER_SIZE);

        // Check for a blank line to terminate early
        if (strlen(buffers[current_line]) == 0) {
            break;
        }

        current_line++;
    }

    printf("\nYou entered:\n");
    for (size_t i = 0; i < current_line; ++i) {
        printf("Line %zu: %s\n", i + 1, buffers[i]);
    }

    return 0;
}
