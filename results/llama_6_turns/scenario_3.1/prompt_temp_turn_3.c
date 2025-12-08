#include <stdio.h>
#include <stdlib.h>

#define MAX_LINES 100 // Define a limit for the number of lines to read
#define BLOCK_SIZE 1024 // Define a block size for dynamic buffer resizing

// Function to dynamically allocate and resize a character array based on a provided size and multiplier
char* reallocate_buffer(char* buf, size_t old_size, size_t new_size) {
    if (new_size <= old_size) { // Avoid unnecessary memory allocation
        return buf;
    }

    char* new_buf = malloc(new_size + 1); // Allocate new buffer with more than enough space for copying and null-terminator
    if (new_buf == NULL) { // Check if reallocation failed
        fprintf(stderr, "Memory reallocation failed in reallocate_buffer (size: %zu)\n", old_size);
        free(buf); // Free the original buffer as it's no longer needed due to memory allocation failure
        return NULL;
    }

    strncpy(new_buf, buf, old_size); // Copy contents from original buffer using safer strncpy function
    new_buf[old_size] = '\0'; // Null-terminate the string

    free(buf); // Free the original buffer after copying its contents

    return new_buf; // Return the newly allocated and resized buffer
}

// Function to read a line of input and dynamically allocate space based on its length
size_t read_line(char** buf, size_t* buf_size) {
    char* input = NULL;
    size_t len = 0;

    while (1) { // Loop until end-of-file is reached
        if (fgets(input, *buf_size + 1, stdin)) { // Read a line of input and store it in the buffer
            break;
        } else {
            free(*buf); // If an error occurs during reading (e.g., end-of-file), free the current buffer
            return 0; // Return 0 to indicate that no more lines can be read due to the error
        }
    }

    if (*buf != NULL) { // If there is already a buffer allocated, reallocate it to fit the new input length plus room for null-terminator
        *buf = reallocate_buffer(*buf, len, strlen(input) + 1);
    } else {
        // Allocate a new buffer that's large enough to hold the entire input string and its null-terminator
        *buf_size = strlen(input) + 1;
        *buf = malloc(*buf_size); // Allocate memory for the buffer

        if (*buf == NULL) { // Check if allocation failed
            fprintf(stderr, "Memory allocation failed in read_line (size: %zu)\n", len);
            return 0; // Return 0 to indicate that no more lines can be read due to the allocation failure
        }
    }

    strcpy(*buf, input); // Copy the contents of the input string into the buffer

    return strlen(input); // Return the length of the read line (excluding null-terminator)
}

int main() {
    char* lines[MAX_LINES]; // Dynamically allocate an array to hold multiple lines
    size_t buf_sizes[MAX_LINES] = { BLOCK_SIZE, 0 }; // Initialize a corresponding array for buffer sizes

    int count = 0; // Track the number of read lines

    while (count < MAX_LINES) {
        if (!fgets(lines[count], buf_sizes[count], stdin)) {
            break;
        }

        printf("Line %d: '%s' (%zu characters)\n", count + 1, lines[count], strlen(lines[count]));

        size_t len = read_line(&lines[count], &buf_sizes[count]);

        if (len == 0) { // If no more lines can be read due to an error
            break;
        }

        count++;
    }

    for (int i = 0; i < count; i++) {
        free(lines[i]); // Free each dynamically allocated line after use
    }

    return 0;
}
