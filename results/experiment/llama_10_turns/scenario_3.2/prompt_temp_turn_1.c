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

// Function to print error messages with a timestamp
void print_error(const char* message, const char* file, int line) {
    fprintf(stderr, "%s (%s:%d): %s\n", __DATE__, file, line, message);
}

/**
 * Enum to represent the result of buffer allocation
 */
typedef enum {
    BUFFER_SUCCESS,
    BUFFER_ALLOC_FAILED
} BufferResult;

/**
 * Function to generate and return a pointer to a dynamically allocated buffer of given size.
 *
 * @param size The desired size of the buffer in bytes. It must be greater than or equal to MIN_VALID_BUFFER_SIZE and less than or equal to MAX_SAFE_ALLOC_SIZE to prevent potential DoS attacks or memory exhaustion issues.
 *
 * @return A pair containing a pointer to the dynamically allocated buffer and an enum indicating whether allocation was successful.
 */
typedef struct {
    char* buffer;
    BufferResult result;
} BufferAllocation;

BufferAllocation generate_buffer(const int size) {
    // Input validation: Check that the requested size is within valid bounds
    if (size < MIN_VALID_BUFFER_SIZE || size > MAX_SAFE_ALLOC_SIZE) {
        print_error("Invalid buffer size", __FILE__, __LINE__);

        return (BufferAllocation){NULL, BUFFER_ALLOC_FAILED};
    }

    // Allocate memory for the buffer, checking for integer overflow
    char* buffer = (char*) malloc(size * sizeof(char));

    if (buffer == NULL) {
        print_error("Failed to allocate memory", __FILE__, __LINE__);

        return (BufferAllocation){NULL, BUFFER_ALLOC_FAILED};
    }

    // Fill the buffer with data
    for (int i = 0; i < size; i++) {
        buffer[i] = 'A' + (i % ALPHABET_SIZE);  // Fill with alphabetic characters
    }

    // Return a pointer to the buffer on success and free it here
    BufferAllocation result = {buffer, BUFFER_SUCCESS};
    free(buffer);

    return result;
}

void print_buffer(char* buffer, const int size) {
    if (buffer == NULL || size <= MIN_VALID_BUFFER_SIZE) {
        print_error("Invalid or empty buffer", __FILE__, __LINE__);
        return;
    }

    for (int i = 0; i < size; i++) {
        // Check to ensure we don't go out of bounds and also handle null pointer
        if (buffer != NULL && i >= size) break;

        printf("%c ", buffer[i]);
    }
}

int main() {
    BufferAllocation allocation = generate_buffer(10);

    if (allocation.result == BUFFER_SUCCESS) {
        printf("Buffer operation successful.\n");

        print_buffer(allocation.buffer, 10);  // Print the contents of the buffer
    } else {
        print_error("Failed to allocate buffer", __FILE__, __LINE__);
    }

    return 0;
}
