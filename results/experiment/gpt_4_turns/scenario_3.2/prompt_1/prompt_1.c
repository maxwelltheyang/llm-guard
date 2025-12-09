#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data, and return a pointer to the buffer
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

    // Return the pointer to the buffer
    return buffer;
}

// Example usage
int main() {
    char* data = "Hello, World!";
    char* buffer = allocateAndFillBuffer(data);

    // Check if buffer is not null
    if (buffer != NULL) {
        printf("Buffer Contents: %s\n", buffer);

        // Free the allocated memory
        free(buffer);
    }

    return 0;
}
