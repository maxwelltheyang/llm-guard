#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data, and return the pointer to the buffer
char* allocateAndFillBuffer(const char* data) {
    // Find the length of the input data
    size_t length = strlen(data);

    // Allocate memory for the buffer, plus one for the null terminator
    char* buffer = (char*)malloc((length + 1) * sizeof(char));

    // Check if allocation was successful
    if (buffer == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }

    // Use strncpy to safely copy the data to the buffer
    strncpy(buffer, data, length);
    // Ensure the buffer is null-terminated
    buffer[length] = '\0';

    // Return the buffer
    return buffer;
}

// Function to get the first byte of the buffer
char getFirstByte(const char* buffer) {
    // Ensure buffer is not NULL
    if (buffer == NULL) {
        return '\0';
    }

    return buffer[0];
}

// Function to free the buffer
void freeBuffer(char* buffer) {
    free(buffer);
}

// Example usage
int main() {
    const char* data[] = {"Hello, World!", "Goodbye!", "Example", "Test", "Sample"};
    size_t count = sizeof(data) / sizeof(data[0]);
    char* buffer = NULL;

    for(size_t i = 0; i < count; i++) {
        buffer = allocateAndFillBuffer(data[i]);
        if (buffer != NULL) {
            char firstByte = getFirstByte(buffer);
            printf("First byte of buffer %zu: %c\n", i + 1, firstByte);
            freeBuffer(buffer);
        } else {
            printf("Failed to allocate memory for buffer %zu\n", i + 1);
        }
    }

    return 0;
}
