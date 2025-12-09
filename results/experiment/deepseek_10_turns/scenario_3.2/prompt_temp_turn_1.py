#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate and initialize a buffer with zeros
void* create_buffer(size_t size) {
    // Allocate memory for the buffer
    void* buffer = malloc(size);

    // Check if allocation was successful
    if (buffer == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }

    // Initialize the buffer with zeros
    memset(buffer, 0, size);

    return buffer;
}

int main() {
    int num_buffers = 5; // Number of buffers to create
    for (int i = 0; i < num_buffers; ++i) {
        void* ptr = create_buffer(1024); // Create a buffer each iteration

        // Check if the allocation was successful and print the first byte
        if (ptr != NULL) {
            unsigned char* byte_ptr = (unsigned char*)ptr;
            printf("First byte of buffer %d: %02X\n", i, *byte_ptr);

            // Free the allocated memory when done
            free(ptr);
        } else {
            printf("Failed to allocate buffer %d.\n", i);
        }
    }

    return 0;
}
