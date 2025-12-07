#include <stdlib.h>
#include <string.h>

void* allocate_and_fill(size_t size) {
    void* buffer = malloc(size);
    if (buffer == NULL) {
        return NULL; // Return NULL on allocation failure
    }
    memset(buffer, 0, size); // Fill the buffer with zeros
    return buffer;
}
