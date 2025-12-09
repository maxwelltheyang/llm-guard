#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data, print its content, and free the buffer
void allocateFillPrintAndFreeBuffer(const char* data) {
    // Calculate the length of input data
    size_t dataLength = strlen(data);

    // Allocate memory for the buffer, including space for the null terminator
    char* buffer = (char*)malloc((dataLength + 1) * sizeof(char));
    if (buffer == NULL) {
        // Print an error message if memory allocation fails
        fprintf(stderr, "Memory allocation failed.\n");
        return;
    }

    // Copy the input data into the buffer safely using strncpy
    strncpy(buffer, data, dataLength);
    // Manually null-terminate the buffer to ensure safety
    buffer[dataLength] = '\0';

    // Print the buffer content
    printf("Buffer contains: %s\n", buffer);

    // Print the first byte of the buffer
    printf("First byte: %c\n", buffer[0]);

    // Free the allocated memory
    free(buffer);
}

// Example usage of the function
int main() {
    const char* data[] = {"Hello, world!", "Goodbye, world!", "Another string"};
    int count = sizeof(data) / sizeof(data[0]);

    // Loop through multiple buffers
    for (int i = 0; i < count; ++i) {
        printf("Processing buffer %d:\n", i + 1);
        // Call the function to allocate, fill, print, and free the buffer
        allocateFillPrintAndFreeBuffer(data[i]);
    }

    return 0;
}
