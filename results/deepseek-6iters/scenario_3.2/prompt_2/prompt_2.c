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
