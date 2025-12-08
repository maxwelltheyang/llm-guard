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
int safe_read_line(char** buf, size_t* buf_size, char* input) {
    // Validate the input string to prevent buffer overflow attacks
    if (strlen(input) >= *buf_size && input[*buf_size - 1] != '\n') { 
        fprintf(stderr, "Buffer overflow detected\n");
        return -1; // Return an error code for buffer overflow
    }

    // Check for trailing newlines or other special characters
    if (input[*buf_size - 1] == '\n' || input[*buf_size - 1] == '\r') {
        fprintf(stderr, "Invalid character detected\n");
        return -2; // Return an error code for invalid characters
    }

    // Attempt to reallocate buffer space if necessary
    char* new_buf = realloc(*buf, strlen(input) + 1);
    if (new_buf != NULL) {
        *buf = new_buf;
        memcpy(*buf, input, strlen(input)); 
    } else {
        fprintf(stderr, "Memory reallocation failed\n");
        return -3; // Return an error code for memory reallocation failure
    }

    return 0; // Return success if no issues encountered
}

int main() {
    char* lines[MAX_LINES]; // Dynamically allocate an array to hold multiple lines
    size_t buf_sizes[MAX_LINES] = { BLOCK_SIZE, 0 }; // Initialize a corresponding array for buffer sizes

    int count = 0; // Track the number of read lines

    while (count < MAX_LINES) {
        char* input = malloc(BLOCK_SIZE); // Dynamically allocate memory for each line
        if (fgets(input, buf_sizes[count], stdin)) { // Read a line of input
            printf("Line %d: '%s' (%zu characters)\n", count + 1, input, strlen(input));

            int len = safe_read_line(&lines[count], &buf_sizes[count], input); // Attempt to read the next line

            if (len == -1 || len == -2 || len == -3) { // If an error occurs during reading
                free(input); 
                break;
            }

            count++;
        } else {
            free(input);
            break; // Exit loop if end-of-file is reached
        }
    }

    for (int i = 0; i < count; i++) {
        free(lines[i]); // Free each dynamically allocated line after use
    }

    return 0;
}
