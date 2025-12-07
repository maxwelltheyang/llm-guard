#include <stdlib.h>
#include <string.h>

char* allocate_buffer(int size) {
    char* buffer = malloc(size);
    if (buffer == NULL) return NULL;

    for (int i = 0; i < size - 1; ++i) {
        buffer[i] = 'a'; // fill with data
    }

    buffer[size - 1] = '\0'; // null terminate

    return buffer;
}
