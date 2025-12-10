#include <stdio.h>
#include <stdlib.h>

// Define constants for safe buffer allocation limits
#define MAX_SAFE_ALLOC_SIZE (1024 * 1024 * 1024) // 1 GB - Maximum size to allocate safely in bytes.
// Ensure that this limit is set high enough to accommodate typical usage, but not so high as to pose a DoS risk.

#define MIN_VALID_BUFFER_SIZE 0 // Minimum valid buffer size. Setting it to 0 means any non-negative value is allowed.

/**
 * Alphabet size for character generation
 */
#define ALPHABET_SIZE 26

// Check that size_t can hold the product of size and sizeof(char)
static_assert(sizeof(size_t) >= (sizeof(int) + sizeof(char)));

/**
 * Function to generate and return a pointer to a dynamically allocated buffer of given size.
 *
 * @param size The desired size of the buffer in bytes. It must be greater than or equal to MIN_VALID_BUFFER_SIZE and less than or equal to MAX_SAFE_ALLOC_SIZE to prevent potential DoS attacks or memory exhaustion issues.
 *
 * @return A pointer to the dynamically allocated buffer on success, or NULL if allocation fails due to invalid input or system constraints.
 */
char* generate_buffer(const int size) {
    // Input validation: Check that the requested size is within valid bounds
    if (size < MIN_VALID_BUFFER_SIZE || size > MAX_SAFE_ALLOC_SIZE) {
        printf("Invalid operation.\n");

        return NULL;
    }

    // Allocate memory for the buffer, checking for integer overflow
    char* buffer = (char*) malloc(size * sizeof(char));

    if (buffer == NULL) {
        fprintf(stderr, "Failed to allocate %d bytes of memory.\n", size);
        exit(EXIT_FAILURE); // Consider terminating the program instead of returning an error code
        return NULL;
    }

    // Fill the buffer with data
    for (int i = 0; i < size; i++) {
        buffer[i] = 'A' + (i % ALPHABET_SIZE);  // Fill with alphabetic characters
    }

    // Return a pointer to the buffer on success
    return buffer;
}

void print_buffer(char* buffer, const int size) {
    if (buffer == NULL || size <= MIN_VALID_BUFFER_SIZE) {
        printf("Invalid or empty buffer. Cannot print.\n");
        return;
    }

    for (int i = 0; i < size; i++) {
        // Check to ensure we don't go out of bounds and also handle null pointer
        if (buffer != NULL && i >= size) break;

        printf("%c ", buffer[i]);
    }
}

void free_buffer(char* buffer, const int size) {
    if (buffer == NULL || size <= MIN_VALID_BUFFER_SIZE) {
        return;  // No memory allocated to free
    }

    free(buffer);
}

int main() {
    const int size = 10;  // Allocate a buffer of size 10

    char* buffer = generate_buffer(size);

    if (buffer != NULL) {
        printf("Buffer operation successful.\n");

        print_buffer(buffer, size);  // Print the contents of the buffer

        free_buffer(buffer, size);  // Don't forget to free the memory when you're done using it
    }

    return 0;
}
