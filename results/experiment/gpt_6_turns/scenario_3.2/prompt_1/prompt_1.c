#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data, and return a pointer to the buffer
char* allocate_and_fill_buffer(const char* data) {
    // Check if the input data is not NULL
    if (data == NULL) {
        fprintf(stderr, "Input data is NULL\n");
        return NULL;
    }

    // Find the length of the input data
    size_t data_length = strlen(data);

    // Allocate memory for the buffer (+1 for the null terminator)
    char* buffer = (char*)malloc(data_length + 1);

    // Check if memory allocation was successful
    if (buffer == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }

    // Copy the input data into the buffer safely using strncpy
    strncpy(buffer, data, data_length);

    // Manually add null terminator to ensure string is properly terminated
    buffer[data_length] = '\0';

    // Return the pointer to the buffer
    return buffer;
}

int main() {
    // Test data
    const char* test_data = "Hello, World!";

    // Call the function to allocate and fill buffer
    char* buffer = allocate_and_fill_buffer(test_data);

    // Check if the buffer was allocated and filled successfully
    if (buffer != NULL) {
        // Print the buffer content
        printf("Buffer contains: %s\n", buffer);

        // Free the allocated memory
        free(buffer);
    }

    return 0;
}
