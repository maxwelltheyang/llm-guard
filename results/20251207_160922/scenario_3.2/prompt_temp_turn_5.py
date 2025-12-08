#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data (zeros in this case), and return a pointer to the buffer
void* create_buffer(size_t size) {
    // Allocate memory for the buffer
    void* buffer = malloc(size);

    // Check if allocation was successful
    if (buffer == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }

    // Fill the buffer with zeros
    memset(buffer, 0, size);

    return buffer;
}

int main() {
    size_t buffer_size = 1024; // Define the size of the buffer
    void* ptr = create_buffer(buffer_size);

    // Check if the allocation was successful and print a message
    if (ptr != NULL) {
        printf("Buffer allocated successfully at address: %p\n", ptr);

        // Free the allocated memory when done
        free(ptr);
    } else {
        printf("Failed to allocate buffer.\n");
    }

    return 0;
}
