#include <stdio.h>
#include <stdlib.h>

#define MEMORY_ALLOCATION_FAILED -1
#define INVALID_BUFFER_SIZE -2
#define BUFFER_OVERFLOW_ERROR -3

char* allocate_buffer(int size) {
    if (size <= 0) {
        // Error: invalid buffer size
        return NULL;
    }

    // Allocate memory for the buffer, checking for overflow conditions
    char* buffer = (char*) malloc(size);

    if (buffer == NULL || size > SIZE_MAX - sizeof(int)) {
        // Memory allocation failed or size is too large
        free(buffer);  // Free the partially allocated memory to prevent leaks
        return (char*) MEMORY_ALLOCATION_FAILED;
    }

    // Fill the buffer with data (in this case, just a string)
    for (int i = 0; i < size - 1; i++) {
        buffer[i] = 'a';
    }

    // Return a pointer to the allocated buffer
    return buffer;
}

void print_buffer(char* buffer) {
    if (buffer != NULL) {
        printf("%s\n", buffer);
        free(buffer);  // Don't forget to free the memory when you're done!
    }
}

int main() {
    char* buffer = allocate_buffer(10);
    print_buffer(buffer);

    return 0;
}
