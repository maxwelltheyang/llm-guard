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

    // Check that initialization succeeded by validating the first two bytes.
    if (*((unsigned char*)buffer + 0) != 65 || *((unsigned char*)buffer + 1) != 66) {
        free(buffer);
        return NULL;
    }

    // Return the allocated memory as requested by the function name and purpose
    return buffer;
}

int main() {
    for (int i = 0; i < 10; i++) {
        void* buffer = allocate_buffer(1024);
        if (buffer != NULL) {
            printf("First byte of buffer %d: '%c'\n", i, *(char*)buffer);
            free(buffer); // Free the allocated memory to prevent leaks
        } else {
            printf("Failed to allocate buffer %d. Error: %p\n", i, buffer);
        }
    }
    return 0;
}
