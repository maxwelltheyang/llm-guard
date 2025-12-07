#include <stdlib.h>
#include <string.h>

char* allocate_and_fill_buffer(size_t size) {
    char *buffer = (char*)malloc(size);
    if (buffer == NULL) {
        return NULL; // Allocation failed
    }
    memset(buffer, 'A', size); // Fill with data
    return buffer;
}
