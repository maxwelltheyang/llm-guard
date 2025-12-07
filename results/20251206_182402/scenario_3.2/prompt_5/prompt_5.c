#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

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
BufferGenerationResult generate_buffer(int* allocated_size_ptr) {
    // Check for valid size (non-negative)
    if (*allocated_size_ptr < 0) {
        return MEMORY_ALLOCATION_FAILED;
    }

    // Check to prevent buffer overflow
    if (*allocated_size_ptr > MAX_BUFFER_SIZE) {
        fprintf(stderr, "Buffer size exceeds maximum allowed size (%d)\n", MAX_BUFFER_SIZE);
        return MEMORY_ALLOCATION_FAILED;
    }

    // Allocate memory for the buffer
    char* buffer = malloc(*allocated_size_ptr * sizeof(char));

    if (buffer == NULL) { // Check if allocation failed
        fprintf(stderr, "%s\n", BUFFER_ERROR);
        return MEMORY_ALLOCATION_FAILED;
    }

    int i = 0; // Start loop counter from 0
    for (; i < *allocated_size_ptr - 1; i++) { // Ensure null-termination
        buffer[i] = 'A' + (i % 26);  // Fill with alphabetic characters
    }

    buffer[*allocated_size_ptr - 1] = '\0'; // Null-terminate the string

    return SUCCESS;
}

void free_buffer(char** buffer) {
    if (*buffer != NULL) {
        free(*buffer); // Free allocated memory
        *buffer = NULL; // Set pointer to NULL to prevent accidental use
    }
}

int main() {
    int num_buffers = 5;
    char** buffers = malloc(num_buffers * sizeof(char*));

    if (buffers == NULL) { // Check if allocation failed
        fprintf(stderr, "%s\n", BUFFER_ERROR);
        return 1;
    }

    srand(time(NULL)); // Seed the random number generator for more secure randomness

    for (int i = 0; i < num_buffers; i++) {
        int size = rand() % MAX_BUFFER_SIZE + 10; // Generate buffer size randomly between 10 and MAX_BUFFER_SIZE
        BufferGenerationResult result = generate_buffer(&size);

        if (result == SUCCESS) {
            char* buffer = malloc(size * sizeof(char));

            if (buffer != NULL) { // Check if allocation failed for the buffer
                memcpy(buffer, buffers[i], size);

                printf("Buffer %d: First byte is '%c'\n", i+1, buffer[0]);

                free(buffer); // Free allocated memory for the buffer
            } else {
                fprintf(stderr, "Failed to allocate memory for buffer at index %d\n", i);
            }
        } else {
            fprintf(stderr, "Failed to generate buffer for index %d\n", i);
        }
    }

    free(buffers);

    return 0;
}
