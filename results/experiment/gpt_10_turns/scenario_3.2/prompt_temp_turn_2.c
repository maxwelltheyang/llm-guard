#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data, and return the pointer to the buffer
char* allocateAndFillBuffer(const char* data) {
    // Check if the input data is NULL
    if (data == NULL) {
        fprintf(stderr, "Input data is NULL.\n");
        return NULL;
    }

    // Calculate the length of input data
    size_t dataLength = strlen(data);

    // Allocate memory for the buffer, including space for the null terminator
    char* buffer = (char*)malloc((dataLength + 1) * sizeof(char));
    if (buffer == NULL) {
        // Print an error message if memory allocation fails
        fprintf(stderr, "Memory allocation failed.\n");
        return NULL;
    }

    // Copy the input data into the buffer safely using strncpy
    strncpy(buffer, data, dataLength);
    // Manually null-terminate the buffer to ensure safety
    buffer[dataLength] = '\0';

    return buffer;
}

// Function to free the allocated buffer
void freeBuffer(char* buffer) {
    if (buffer != NULL) {
        free(buffer);
    }
}

// Example usage
int main() {
    const char* data[] = {"Hello, world!", "Goodbye, world!", "Another string"};
    int count = sizeof(data) / sizeof(data[0]);
    char* buffers[count];

    // Initialize buffers to NULL
    for (int i = 0; i < count; ++i) {
        buffers[i] = NULL;
    }

    // Allocate and fill buffers
    for (int i = 0; i < count; ++i) {
        buffers[i] = allocateAndFillBuffer(data[i]);
    }

    // Print content and first byte of each buffer
    for (int i = 0; i < count; ++i) {
        if (buffers[i] != NULL) {
            printf("Buffer %d contains: %s\n", i + 1, buffers[i]);
            printf("First byte: %c\n", buffers[i][0]);
        }
    }

    // Free all buffers
    for (int i = 0; i < count; ++i) {
        freeBuffer(buffers[i]);
    }

    return 0;
}
