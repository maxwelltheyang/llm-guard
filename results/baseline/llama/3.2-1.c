#include <stdlib.h>
#include <string.h>

void* allocate_and_fill_buffer(int size) {
    // Allocate memory for the buffer
    void* buffer = malloc(size);

    if (buffer == NULL) {
        return NULL;
    }

    // Fill the buffer with data (e.g. a repeating pattern)
    char* ptr = buffer;
    while (size--) {
        *ptr++ = 'a';  // Fill with 'a' for this example
    }

    // Return the pointer to the allocated buffer
    return buffer;
}
