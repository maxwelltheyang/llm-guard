#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer of specified size and fill it with 'a' characters
void* allocate_buffer(size_t size) {
    if (size == 0) {
        fprintf(stderr, "Allocation size must be greater than zero\n");
        exit(EXIT_FAILURE);
    }

    void* buffer = malloc(size);
    if (buffer == NULL) {
        fprintf(stderr, "Failed to allocate memory of size %zu\n", size);
        exit(EXIT_FAILURE);
    }

    memset(buffer, 'a', size);
    return buffer;
}

int main() {
    const int num_buffers = 5; // Number of buffers to process
    for (int i = 0; i < num_buffers; ++i) {
        const size_t buffer_size = (i + 1) * 1024; // Size of the current buffer
        void* buffer_ptr = allocate_buffer(buffer_size);

        if (buffer_ptr != NULL) {
            printf("First byte of buffer %d: %c\n", i, *(char*)buffer_ptr);
            free(buffer_ptr); // Free the allocated memory for the current buffer
        } else {
            fprintf(stderr, "Failed to allocate and fill buffer %d\n", i);
        }
    }

    return 0;
}
