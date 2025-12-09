#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data, and return the first byte
char allocateFillAndGetFirstByte(const char* data) {
    // Find the length of the input data
    size_t length = strlen(data);

    // Allocate memory for the buffer, plus one for the null terminator
    char* buffer = (char*)malloc((length + 1) * sizeof(char));

    // Check if allocation was successful
    if (buffer == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return '\0';  // Return null character if allocation fails
    }

    // Use strncpy to safely copy the data to the buffer
    strncpy(buffer, data, length);
    // Ensure the buffer is null-terminated
    buffer[length] = '\0';

    // Get the first byte of the buffer
    char firstByte = buffer[0];

    // Free the allocated memory
    free(buffer);

    // Return the first byte
    return firstByte;
}

// Example usage
int main() {
    const char* data[] = {"Hello, World!", "Goodbye!", "Example", "Test", "Sample"};
    size_t count = sizeof(data) / sizeof(data[0]);

    for(size_t i = 0; i < count; i++) {
        char firstByte = allocateFillAndGetFirstByte(data[i]);
        if (firstByte != '\0') {
            printf("First byte of buffer %zu: %c\n", i + 1, firstByte);
        } else {
            printf("Failed to allocate memory for buffer %zu\n", i + 1);
        }
    }

    return 0;
}
