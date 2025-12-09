#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data, and return a pointer to the buffer
void* allocate_and_fill_buffer(size_t size) {
    if (size == 0) {
        fprintf(stderr, "Allocation size must be greater than zero\n");
        exit(EXIT_FAILURE);
    }

    void* buffer = malloc(size);
    if (buffer == NULL) {
        fprintf(stderr, "Failed to allocate memory of size %zu\n", size);
        exit(EXIT_FAILURE);
    }

    memset(buffer, 'a', size);
    return buffer;
}

int main() {
    size_t size = 1024; // Example size
    void* ptr = allocate_and_fill_buffer(size);

    printf("First 10 bytes: ");
    for (size_t i = 0; i < 10 && i < size; ++i) {
        putchar(*((char*)ptr + i));
    }
    putchar('\n');

    free(ptr); // Free the allocated memory encapsulated within the function

    return 0;
}
