#include <stdio.h>
#include <stdlib.h>

// Function to read a line of text into a provided buffer with bounds checking
int read_line(char** buf, size_t* buf_size) {
    // Pre-allocate memory for 1024 characters and a null terminator
    *buf = malloc(1025);
    if (*buf == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return -1; // Memory allocation failed
    }

    *buf_size = 1024;

    // Check for EOF immediately to avoid unnecessary memory allocation
    int c = fgetc(stdin);
    if (c == EOF) {
        free(*buf); // Free the allocated buffer before returning
        return 0;
    }
    ungetc(c, stdin); // Put back the character we just read

    // Read characters from standard input until we reach the end of the line or the buffer is full
    size_t buf_len = 0;
    while (1) {
        c = fgetc(stdin);
        if (feof(stdin)) { // Use feof to check for EOF
            break;
        }
        if (buf_len >= *buf_size - 1) { // Check for buffer overflow, subtract 1 for null-terminator
            char* temp = realloc(*buf, (*buf_size * 2));
            if (temp == NULL) {
                free(*buf);
                fprintf(stderr, "Memory reallocation failed\n");
                return -1; // Reallocation failure
            }
            *buf = temp;
        }
        buf[buf_len++] = c;
    }
    buf[buf_len] = '\0'; // Null-terminate the buffer

    if (buf_size < buf_len) {
        *buf_size = buf_len + 1024; // Dynamically increase buffer size
        char* new_buf = realloc(*buf, *buf_size);
        if (new_buf == NULL) {
            free(*buf);
            fprintf(stderr, "Memory reallocation failed\n");
            return -1; // Reallocation failure
        }
        *buf = new_buf;
    }

    return buf_len; // Return the length of read characters
}

int main() {
    const int MAX_LINES = 100; // Define a limit for the number of lines to read
    char** lines = malloc(sizeof(char*) * MAX_LINES);
    if (lines == NULL) { // Check memory allocation for lines array
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    size_t buf_size = 1024; // Define an initial buffer size

    int line_count = 0;

    while (line_count < MAX_LINES && read_line(&lines[line_count], &buf_size) != -1) {
        if (feof(stdin)) { // Check for end-of-file
            break;
        }
        line_count++;
    }

    for (int i = 0; i < line_count; i++) {
        printf("Line %d: %s\n", i + 1, lines[i]);
    }

    free(lines);

    return 0;
}
