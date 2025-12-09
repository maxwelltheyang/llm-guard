#include <stdio.h>
#include <stdlib.h>

// Function to read a line of text into a provided buffer with bounds checking
int read_line(char** buf, size_t* buf_size) {
    // Initialize the initial buffer size to 1024 bytes
    *buf = malloc(1024);
    if (*buf == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return -1; // Memory allocation failed
    }

    *buf_size = 1024;

    // Read characters from standard input until we reach the end of the line or the buffer is full
    int c;
    size_t buf_len = 0;
    while ((c = fgetc(stdin)) != EOF) {
        if (buf_len >= *buf_size - 1) { // Check for buffer overflow, subtract 1 for null-terminator
            char* temp = realloc(*buf, (*buf_size * 2));
            if (temp == NULL) {
                free(*buf);
                fprintf(stderr, "Memory reallocation failed\n");
                return -1; // Memory reallocation failed
            }
            *buf = temp;
            *buf_size *= 2;
        }

        char* ptr = realloc(*buf, (*buf_size + 1));
        if (ptr == NULL) {
            free(*buf);
            fprintf(stderr, "Memory reallocation failed\n");
            return -1; // Memory reallocation failed
        }
        *buf = ptr;

        // Store the character in the buffer only if it's not a null character
        (*buf)[buf_len] = c;
        buf_len++;

        // Use snprintf to safely copy characters into the buffer, leaving space for the null-terminator
        char* temp_buf = realloc(*buf, *buf_size + 1);
        if (temp_buf == NULL) {
            free(*buf);
            fprintf(stderr, "Memory reallocation failed\n");
            return -1; // Memory reallocation failed
        }
        *buf = temp_buf;
        snprintf((*buf) + buf_len, *buf_size - buf_len, "%c", c);
    }

    // Null-terminate the string
    (*buf)[buf_len] = '\0';

    return buf_len;
}

int main() {
    char* input;
    size_t len;

    int read_len = read_line(&input, &len);

    if (read_len == -1) { // Handle memory allocation or reallocation failure
        fprintf(stderr, "Memory error\n");
        exit(1);
    }

    printf("Read %d characters: %s\n", read_len, input);

    free(input); // Don't forget to free the dynamically allocated memory

    return 0;
}
