#include <stdlib.h>
#include <string.h>

void* allocate_buffer(int size) {
    // Check for integer overflow when calculating memory sizes
    if (size <= 0 || size > INT_MAX - 1) {
        return NULL;
    }

    // Allocate memory for the buffer
    void* buffer = malloc(size);

    if (buffer == NULL) {  
        return NULL;  // Directly handle failure to allocate, no need to free in this case
    }

    // Check that the allocated memory can be accessed safely and was actually allocated
    if ((uintptr_t)buffer & (sizeof(void*) - 1)) {
        free(buffer); 
        return NULL;
    }

    // Initialize the buffer with a string of 'A's
    memset(buffer, 'A', size);

    return buffer;
}
