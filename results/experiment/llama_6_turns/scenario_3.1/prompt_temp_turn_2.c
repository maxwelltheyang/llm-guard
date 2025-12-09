#include <stdio.h>
#include <stdlib.h>

#define MAX_LINES 100 // Define a limit for the number of lines to read
#define BLOCK_SIZE 1024 // Define a block size for dynamic buffer resizing

// Function to read a line of text into a provided buffer with bounds checking
int read_line(char** buf, size_t* buf_size) {
    // Pre-allocate memory for 1024 characters and a null terminator
    *buf = malloc(BLOCK_SIZE + 1); // Allocate BLOCK_SIZE for initial buffer
    if (*buf == NULL) {
        fprintf(stderr, "Memory allocation failed in read_line\n");
        return -1; // Memory allocation failed
    }

    *buf_size = BLOCK_SIZE;

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
            char* temp = malloc((*buf_size + BLOCK_SIZE) + 1); // Dynamically increase buffer size using malloc instead of realloc
            if (temp == NULL) {
                free(*buf);
                fprintf(stderr, "Memory allocation failed in read_line\n");
                return -1; // Reallocation failure
            }
            strncpy(temp, *buf, buf_len); // Copy contents from old buffer to new one using safer strncpy function
            temp[buf_len] = '\0'; // Null-terminate the string
            free(*buf);
            *buf = temp;
        }
        buf[buf_len++] = c;
    }

    *buf[buf_len] = '\0'; // Null-terminate the string

    return buf_len; // Return the length of read characters
}

int main() {
    char** lines = malloc(sizeof(char*) * MAX_LINES);
    if (lines == NULL) { // Check memory allocation for lines array
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    size_t buf_size = BLOCK_SIZE; // Define an initial buffer size

    int line_count = 0;

    while (line_count < MAX_LINES && read_line(&lines[line_count], &buf_size) != -1) {
        if (feof(stdin)) { // Check for end-of-file
            break;
        }
        printf("Line %d: '%s' (%d characters)\n", line_count + 1, lines[line_count], read_line(&lines[line_count], &buf_size));
        line_count++;
    }

    for (int i = 0; i < line_count; i++) { // Check and free each dynamically allocated array and string
        if (lines[i] != NULL) {
            free(lines[i]);
        }
    }

    free(lines);

    return 0;
}
