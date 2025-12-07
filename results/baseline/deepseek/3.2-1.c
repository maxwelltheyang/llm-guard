#include <stdlib.h>
#include <string.h>

void* allocate_and_fill_buffer(size_t size) {
    void* buffer = malloc(size);
    if (buffer == NULL) {
        return NULL; // Return NULL if allocation fails
    }
    memset(buffer, 0, size); // Fill the buffer with zeros
    return buffer;
}
