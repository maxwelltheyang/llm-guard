#include <stdio.h>
#include <stdlib.h>

#define MEMORY_ALLOCATION_FAILED -1
#define INVALID_BUFFER_SIZE -2
#define BUFFER_OVERFLOW_ERROR -3

char* allocate_buffer(int size) {
    if (size <= 0) {
        // Error: invalid buffer size
        return NULL;
    }

    char* buffer = malloc(size);

    if (buffer == NULL || size > SIZE_MAX - sizeof(int)) {
        free(buffer);  
        return (char*) MEMORY_ALLOCATION_FAILED;
    }

    for (int i = 0; i < size - 1; i++) {
        buffer[i] = 'a';
    }

    return buffer;
}

void print_buffer(char* buffer) {
    if (buffer != NULL && *buffer != '\0') { // Check if the buffer is valid
        printf("%s\n", buffer);
        free(buffer);  // Don't forget to free the memory when you're done!
    } else {
        printf("Memory allocation failed for this buffer.\n");
    }
}

int main() {
    int num_buffers = 5;
    for (int i = 0; i < num_buffers; i++) {
        char* buffer = allocate_buffer(10);
        if (buffer != MEMORY_ALLOCATION_FAILED) {
            printf("First byte of buffer %d: ", i);
            printf("%c\n", *(buffer));
            print_buffer(buffer);
        } else {
            printf("Memory allocation failed for buffer %d\n", i);
        }
    }

    return 0;
}
