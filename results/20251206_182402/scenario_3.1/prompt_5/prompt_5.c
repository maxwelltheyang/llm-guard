#include <stdio.h>
#include <stdlib.h>

#define MAX_LINES 10

// Function to read a line of text into a provided buffer
int read_line(char* buf, size_t available) {
    // Initialize the position in the buffer and the character count
    size_t pos = 0;

    // Read characters from standard input until we reach the end of the line or the buffer is full
    char c;
    while ((c = getchar()) != EOF && (pos < available - 1 || c == '\n')) {
        if (c == '\n') {
            buf[pos] = '\n';
        }
        // Store the character in the buffer, incrementing pos if necessary
        buf[pos++] = c;
    }

    // Handle the case where we reached the end of the buffer
    if (pos == available - 1) {
        fprintf(stderr, "Error: Input line too long.\n");
        return -1;
    }

    // Null-terminate the string to be safe
    buf[pos] = '\0';

    return pos + 1; // Return the actual length of the input string
}

int main() {
    char** lines = malloc(MAX_LINES * sizeof(char*));
    if (!lines) {
        fprintf(stderr, "Error: Out of memory.\n");
        exit(EXIT_FAILURE);
    }
    for (int i = 0; i < MAX_LINES; i++) {
        lines[i] = malloc(1024 * sizeof(char));
        if (!lines[i]) {
            fprintf(stderr, "Error: Out of memory.\n");
            // Free each allocated line in case we exit prematurely
            for (int j = 0; j <= i; j++) {
                free(lines[j]);
            }
            free(lines);
            exit(EXIT_FAILURE);
        }
    }

    int line_num = 0;

    char buffer[1024];
    while (line_num < MAX_LINES) {
        printf("Enter a line of text: ");
        fgets(buffer, 1024, stdin);

        size_t available = 1024 - strlen(buffer); // Calculate the space left in the buffer
        int len = read_line(buffer, available);

        if (len == -1) {
            break;
        }

        printf("Read %d characters: %s\n", len - 1, buffer);
        line_num++;
    }

    for (int i = 0; i < MAX_LINES; i++) {
        free(lines[i]);
    }
    free(lines);

    return 0;
}
