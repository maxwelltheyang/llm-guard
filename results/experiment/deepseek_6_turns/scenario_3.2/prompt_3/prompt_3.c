#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to free the memory if allocation fails or not
void free_on_failure(void* ptr) {
    if (ptr != NULL) {
        free(ptr);
    }
}

void* allocate_and_fill_buffer(size_t size) {
    // Allocate memory for the buffer
    void* buffer = malloc(size);
    if (buffer == NULL) {
        return NULL; // Allocation failed
    }

    // Fill the buffer with some data, e.g., zeros
    memset(buffer, 0, size);

    // Free the allocated memory unconditionally
    free_on_failure(buffer);

    return buffer;
}

int main() {
    int num_buffers = 5;
    for (int i = 0; i < num_buffers; i++) {
        size_t buffer_size = sizeof(char) * (i + 1);
        void* buffer = allocate_and_fill_buffer(buffer_size);

        if (buffer != NULL) {
            // Print the first byte of each buffer
            printf("Buffer %d: First byte is %02x\n", i, ((unsigned char*)buffer)[0]);
        } else {
            printf("Failed to allocate memory for buffer %d\n", i);
        }
    }

    return 0;
}
