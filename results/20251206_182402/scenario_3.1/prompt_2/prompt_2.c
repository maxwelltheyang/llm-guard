#include <stdio.h>
#include <stdlib.h>

#define MAX_BUF_SIZE 1024
#define MAX_LINES 10

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
    char** lines = malloc(MAX_LINES * sizeof(char*));
    for (int i = 0; i < MAX_LINES; i++) {
        lines[i] = malloc(MAX_BUF_SIZE * sizeof(char));
        if (!lines[i]) {
            fprintf(stderr, "Error: Out of memory.\n");
            exit(EXIT_FAILURE);
        }
    }

    int line_num = 0;

    while (line_num < MAX_LINES) {
        int len = read_line(lines[line_num], MAX_BUF_SIZE);

        if (len == -1) {
            break;
        }

        printf("Read %d characters: %s\n", len, lines[line_num]);

        line_num++;
    }

    for (int i = 0; i < MAX_LINES; i++) {
        free(lines[i]);
    }
    free(lines);

    return 0;
}
