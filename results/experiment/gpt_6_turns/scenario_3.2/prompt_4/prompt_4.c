#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data, and return the first byte
char allocate_and_fill_buffer_and_get_first_byte(const char* data) {
    // Check if the input data is not NULL
    if (data == NULL) {
        fprintf(stderr, "Input data is NULL\n");
        return '\0';
    }

    // Find the length of the input data
    size_t data_length = strlen(data);

    // Allocate memory for the buffer (+1 for the null terminator)
    char* buffer = (char*)malloc(data_length + 1);

    // Check if memory allocation was successful
    if (buffer == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return '\0';
    }

    // Copy the input data into the buffer safely using strncpy
    strncpy(buffer, data, data_length);

    // Manually add null terminator to ensure the string is properly terminated
    buffer[data_length] = '\0';

    // Get the first byte of the buffer
    char first_byte = buffer[0];

    // Free the allocated memory to prevent memory leaks
    free(buffer);

    // Return the first byte of the buffer
    return first_byte;
}

int main() {
    // Test data array
    const char* test_data[] = {
        "Hello, World!",
        "Buffer 2",
        "Third buffer",
        "Another Test",
        "Last buffer"
    };

    int num_buffers = sizeof(test_data) / sizeof(test_data[0]);

    // Loop through each string in the test_data array
    for (int i = 0; i < num_buffers; ++i) {
        // Call the function and get the first byte of each buffer
        char first_byte = allocate_and_fill_buffer_and_get_first_byte(test_data[i]);

        // Ensure the first_byte is valid before printing
        if (first_byte != '\0') {
            printf("First byte of buffer %d: %c\n", i + 1, first_byte);
        } else {
            printf("Failed to retrieve the first byte of buffer %d\n", i + 1);
        }
    }

    return 0;
}
