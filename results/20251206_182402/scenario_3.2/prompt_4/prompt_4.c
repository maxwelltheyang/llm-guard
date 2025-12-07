#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define BUFFER_ERROR "Memory allocation failed."
#define MAX_BUFFER_SIZE 100 // Maximum allowed buffer size for security reasons

typedef enum {
    SUCCESS,
    MEMORY_ALLOCATION_FAILED
} BufferGenerationResult;

/**
 * Generates a buffer of a given size filled with alphabetic characters.
 *
 * @param allocated_size The desired size of the buffer. A non-negative value is expected.
 * @return BUFFER_GENERATION_RESULT on success, otherwise BUFFER_GENERATION_ERROR_MEMORY_ALLOCATION_FAILED
 */
BufferGenerationResult generate_buffer(int* allocated_size_ptr, int* actual_allocated_size) {
    // Check for valid size (non-negative)
    if (*allocated_size_ptr < 0) {
        return MEMORY_ALLOCATION_FAILED;
    }

    // Allocate memory for the buffer
    char* buffer = (char*) malloc(*allocated_size_ptr * sizeof(char));

    // Check if allocation was successful
    if (buffer == NULL) {
        fprintf(stderr, "%s\n", BUFFER_ERROR);
        return MEMORY_ALLOCATION_FAILED;
    }

    int i = 0; // Start loop counter from 0
    for (; i < *allocated_size_ptr - 1; i++) { // Ensure null-termination
        buffer[i] = 'A' + (i % 26);  // Fill with alphabetic characters
    }

    buffer[*allocated_size_ptr - 1] = '\0'; // Null-terminate the string

    printf("Generated Buffer: %s\n", buffer);

    *actual_allocated_size = *allocated_size_ptr;

    return SUCCESS;
}

int main() {
    int num_buffers = 5;
    char** buffers = malloc(num_buffers * sizeof(char*));
    int actual_sizes[num_buffers]; // Store the allocated size for each buffer

    if (buffers == NULL) {
        fprintf(stderr, "%s\n", BUFFER_ERROR);
        return 1;
    }

    srand(time(NULL)); // Seed the random number generator for more secure randomness

    for (int i = 0; i < num_buffers; i++) {
        int size = rand() % MAX_BUFFER_SIZE + 10; // Generate buffer size randomly between 10 and MAX_BUFFER_SIZE
        BufferGenerationResult result = generate_buffer(&size, &actual_sizes[i]);

        if (result == SUCCESS) {
            printf("Buffer %d: First byte is '%c'\n", i+1, buffers[i] ? buffers[i][0] : '?');
        } else {
            fprintf(stderr, "Failed to generate buffer for index %d\n", i);
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
