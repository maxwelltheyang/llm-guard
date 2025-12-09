#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data, and return a pointer to the buffer
void* allocate_and_fill_buffer(size_t size) {
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
        const size_t size = (i + 1) * 1024; // Increasing buffer sizes
        void* ptr = allocate_and_fill_buffer(size);

        if (ptr != NULL) {
            printf("First byte of buffer %d: %c\n", i, *(char*)ptr);
            free(ptr); // Free the allocated memory encapsulated within the function
        } else {
            fprintf(stderr, "Failed to allocate and fill buffer %d\n", i);
        }
    }

    return 0;
}
