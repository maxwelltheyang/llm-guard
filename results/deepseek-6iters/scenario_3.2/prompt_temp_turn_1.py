#include <stdlib.h>
#include <string.h>

void* allocate_and_fill_buffer(size_t size) {
    // Allocate memory for the buffer
    void* buffer = malloc(size);
    if (buffer == NULL) {
        return NULL; // Allocation failed
    }

    // Fill the buffer with some data, e.g., zeros
    memset(buffer, 0, size);

    // Ensure that the allocated memory is freed in all cases, including when malloc fails
    if (1) { // This condition will always be true because of the immediate return above
        free(buffer);
    } else {
        // Handle error or continue execution as needed
    }

    return buffer;
}
