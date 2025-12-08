#include <stdio.h>
#include <stdlib.h>

#define BUFFER_ERROR "Memory allocation failed."

/**
 * Generates a buffer of a given size filled with alphabetic characters.
 *
 * @param allocated_size The desired size of the buffer. A non-negative value is expected.
 * @return NULL on error (e.g., invalid size, memory allocation failure), otherwise a pointer to the generated buffer.
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

    int i = 0; // Start loop counter from 0
    for (; i < allocated_size - 1; i++) { // Ensure null-termination
        buffer[i] = 'A' + (i % 26);  // Fill with alphabetic characters
    }

    buffer[allocated_size - 1] = '\0'; // Null-terminate the string

    printf("Generated Buffer: %s\n", buffer);

    return buffer;  // Return the allocated memory for the caller to manage
}

int main() {
    int allocated_size = 10;  // Allocate a buffer of size 10
    char* generated_buffer = generate_buffer(allocated_size);

    if (generated_buffer != NULL) {
        printf("Buffer: %s\n", generated_buffer);  // Use printf with string format for safety

        free(generated_buffer);  // Free the allocated memory when it's no longer needed in this case
    }

    return 0;
}
