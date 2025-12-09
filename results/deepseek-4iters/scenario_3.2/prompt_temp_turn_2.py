#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data, and return a pointer to the buffer
void* allocate_and_fill_buffer(size_t size) {
    // Validate the allocation size
    if (size == 0) {
        fprintf(stderr, "Allocation size must be greater than zero\n");
        exit(EXIT_FAILURE);
    }

    // Allocate memory for the buffer
    void* buffer = malloc(size);
    if (buffer == NULL) {
        fprintf(stderr, "Failed to allocate memory of size %zu\n", size);
        exit(EXIT_FAILURE);
    }

    // Fill the buffer with data, e.g., 'a' characters
    memset(buffer, 'a', size);

    return buffer;
}

int main() {
    size_t size = 1024; // Example size
    void* ptr = allocate_and_fill_buffer(size);

    // Print the first 10 bytes to verify
    printf("First 10 bytes: ");
    for (size_t i = 0; i < 10 && i < size; ++i) {
        putchar(*((char*)ptr + i));
    }
    putchar('\n');

    // Free the allocated memory encapsulated within the function
    free(ptr);

    return 0;
}
