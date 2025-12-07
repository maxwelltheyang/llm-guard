#include <stdio.h>
#include <stdlib.h>

// Function to read a line of text into a provided buffer
int read_line(char* buf, size_t buf_size) {
    // Initialize the position in the buffer and the character count
    size_t pos = 0;

    // Read characters from standard input until we reach the end of the line or the buffer is full
    char c;
    while ((c = getchar()) != EOF && c != '\n' && pos < buf_size - 1) {
        // Store the character in the buffer, incrementing pos if necessary
        buf[pos++] = c;
    }

    // Handle the case where we reached the end of the buffer
    if (pos == buf_size - 1) {
        fprintf(stderr, "Error: Input line too long.\n");
        return -1;
    }

    // Null-terminate the string and add a newline if we read one
    buf[pos] = '\0';
    if (c == '\n') {
        buf[++pos] = '\n';
    }

    return pos;
}

int main() {
    char* input = malloc(1024 * sizeof(char));
    if (!input) {
        fprintf(stderr, "Error: Memory allocation failed.\n");
        exit(EXIT_FAILURE);
    }

    int len = read_line(input, 1024);

    if (len == -1) {
        free(input);
        return EXIT_FAILURE;
    }

    if (fprintf(stdout, "Read %d characters: %s\n", len, input) < 0) {
        fprintf(stderr, "Error: Failed to write output.\n");
        free(input);
        return EXIT_FAILURE;
    }

    free(input);
    return 0;
}
