#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data, and output its contents
// The buffer is freed inside the function to prevent memory leaks
void allocate_and_fill_buffer(const char* data) {
    // Check if the input data is not NULL
    if (data == NULL) {
        fprintf(stderr, "Input data is NULL\n");
        return;
    }

    // Find the length of the input data
    size_t data_length = strlen(data);

    // Allocate memory for the buffer (+1 for the null terminator)
    char* buffer = (char*)malloc(data_length + 1);

    // Check if memory allocation was successful
    if (buffer == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return;
    }

    // Copy the input data into the buffer safely using strncpy
    strncpy(buffer, data, data_length);

    // Manually add null terminator to ensure the string is properly terminated
    buffer[data_length] = '\0';

    // Use the buffer (e.g., print it)
    printf("Buffer contains: %s\n", buffer);

    // Free the allocated memory to prevent memory leaks
    free(buffer);
}

int main() {
    // Test data
    const char* test_data = "Hello, World!";

    // Call the function to allocate and fill buffer
    allocate_and_fill_buffer(test_data);

    return 0;
}
