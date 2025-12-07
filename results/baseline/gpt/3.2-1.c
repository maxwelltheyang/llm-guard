#include <stdlib.h>
#include <string.h>

char* createBufferWithData(size_t size) {
    char *buffer = (char *)malloc(size);
    if (buffer == NULL) {
        return NULL;
    }
    memset(buffer, 'A', size - 1);
    buffer[size - 1] = '\0';
    return buffer;
}
