#include <stdio.h>
#include <stdlib.h>

#define BUFFER_ERROR "Memory allocation failed."

/**
 * Generates a buffer of a given size filled with alphabetic characters.
 *
 * @param allocated_size The desired size of the buffer. A non-negative value is expected.
 * @return NULL on error (e.g., invalid size, memory allocation failure), otherwise a pointer to the buffer.
 */
char* generate_buffer(int allocated_size) {
    // Check for valid size (non-negative)
    if (allocated_size < 0) {
        return NULL;  // Return error immediately
    }

    // Allocate memory for the buffer
    char* buffer = (char*) malloc(allocated_size * sizeof(char));

    // Check if allocation was successful
    if (buffer == NULL) {
        fprintf(stderr, "%s\n", BUFFER_ERROR);
        return NULL;
    }

    // Fill the buffer with data
    int i = 0;
    for (; i < allocated_size; i++) {
        buffer[i] = 'A' + (i % 26);  // Fill with alphabetic characters
    }

    // Null-terminate the string to prevent potential overflows or errors
    buffer[allocated_size] = '\0';

    // Return a pointer to the buffer
    return buffer;
}

int main() {
    int allocated_size = 10;  // Allocate a buffer of size 10
    char* buffer = generate_buffer(allocated_size);

    if (buffer != NULL) {
        printf("Buffer: %s\n", buffer);  // Use printf with string format for safety

        // Don't forget to free the allocated memory when done!
        free(buffer);
    }

    return 0;
}
