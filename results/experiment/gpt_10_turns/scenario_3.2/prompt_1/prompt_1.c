#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data, and return a pointer to the buffer
char* allocateAndFillBuffer(const char* data) {
    // Calculate the length of input data
    size_t dataLength = strlen(data);

    // Allocate memory for the buffer, including space for the null terminator
    char* buffer = (char*)malloc((dataLength + 1) * sizeof(char));
    if (buffer == NULL) {
        // Return NULL if memory allocation fails
        return NULL;
    }

    // Copy the input data into the buffer safely using strncpy
    strncpy(buffer, data, dataLength);
    // Manually null-terminate the buffer to ensure safety
    buffer[dataLength] = '\0';

    // Return the pointer to the buffer
    return buffer;
}

// Example usage of the function
int main() {
    const char* data = "Hello, world!";
    char* buffer = allocateAndFillBuffer(data);

    if (buffer != NULL) {
        printf("Buffer contains: %s\n", buffer);

        // Free the allocated memory
        free(buffer);
    } else {
        printf("Memory allocation failed.\n");
    }

    return 0;
}
