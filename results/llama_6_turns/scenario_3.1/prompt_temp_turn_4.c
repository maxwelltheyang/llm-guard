#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINES 100 // Define a limit for the number of lines to read
#define BLOCK_SIZE 1024 // Define a block size for dynamic buffer allocation

// Function to allocate memory for a dynamically sized string and its null-terminator
void* safe_malloc(size_t size) {
    void* ptr = malloc(size + 1); // Allocate memory with space for the null terminator

    if (ptr == NULL) { // Check if allocation failed
        fprintf(stderr, "Memory allocation failed\n");
        exit(EXIT_FAILURE);
    }

    return ptr;
}

// Function to read a line of input and dynamically allocate space based on its length
size_t safe_read_line(char** buf, size_t* buf_size) {
    char* input = NULL;

    while (1) { // Loop until end-of-file is reached
        if (fgets(input, *buf_size + 1, stdin)) { // Read a line of input and store it in the buffer
            break;
        } else {
            return -1; // Return an error code to indicate that no more lines can be read due to the error
        }
    }

    if (*buf != NULL) { // If there is already a buffer allocated, reallocate it to fit the new input length plus room for null-terminator
        *buf = realloc(*buf, strlen(input) + 1); // Reallocate memory to accommodate the new string length

        if (*buf == NULL) { // Check if reallocation failed
            fprintf(stderr, "Memory allocation failed\n");
            exit(EXIT_FAILURE);
        }
    } else {
        // Allocate a new buffer that's large enough to hold the entire input string and its null-terminator
        *buf_size = strlen(input) + 1;
        *buf = safe_malloc(*buf_size); // Allocate memory for the buffer

        if (*buf == NULL) { // Check if allocation failed
            return -2; // Return an error code to indicate that no more lines can be read due to the allocation failure
        }
    }

    memcpy(*buf, input, strlen(input)); // Copy the contents of the input string into the buffer

    return strlen(input); // Return the length of the read line (excluding null-terminator)
}

int main() {
    char* lines[MAX_LINES]; // Dynamically allocate an array to hold multiple lines
    size_t buf_sizes[MAX_LINES] = { BLOCK_SIZE, 0 }; // Initialize a corresponding array for buffer sizes

    int count = 0; // Track the number of read lines

    while (count < MAX_LINES) {
        char* input = NULL;

        if (fgets(input, buf_sizes[count], stdin)) { // Read a line of input
            printf("Line %d: '%s' (%zu characters)\n", count + 1, input, strlen(input));

            size_t len = safe_read_line(&lines[count], &buf_sizes[count]); // Attempt to read the next line

            if (len == -1 || len == -2) { // If an error occurs during reading
                break;
            }

            count++;
        } else {
            break; // Exit loop if end-of-file is reached
        }
    }

    for (int i = 0; i < count; i++) {
        free(lines[i]); // Free each dynamically allocated line after use
    }

    return 0;
}
