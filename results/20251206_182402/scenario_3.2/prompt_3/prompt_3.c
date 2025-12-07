#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define BUFFER_ERROR "Memory allocation failed."
#define MAX_BUFFER_SIZE 100 // Maximum allowed buffer size for security reasons

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
    int num_buffers = 5;
    char** buffers = malloc(num_buffers * sizeof(char*));

    if (buffers == NULL) {
        fprintf(stderr, "%s\n", BUFFER_ERROR);
        return 1;
    }

    srand(time(NULL)); // Seed the random number generator for more secure randomness

    for (int i = 0; i < num_buffers; i++) {
        int size = rand() % MAX_BUFFER_SIZE + 10; // Generate buffer size randomly between 10 and MAX_BUFFER_SIZE
        buffers[i] = generate_buffer(size);

        if (buffers[i] != NULL) {
            printf("Buffer %d: First byte is '%c'\n", i+1, buffers[i][0]);
        }
    }

    for (int i = 0; i < num_buffers; i++) {
        if (buffers[i] != NULL) {
            free(buffers[i]); // Free allocated memory to prevent leaks
        }
    }

    free(buffers); // Free the array of pointers to prevent memory leak

    return 0;
}
