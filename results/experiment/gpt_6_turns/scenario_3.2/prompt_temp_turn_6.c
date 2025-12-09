#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to allocate a buffer, fill it with data, and return the buffer
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

    // Manually add null terminator to ensure the string is properly terminated
    buffer[data_length] = '\0';

    // Return the buffer
    return buffer;
}

// Function to get the first byte of the buffer
char get_first_byte_of_buffer(const char* buffer) {
    if (buffer == NULL) {
        fprintf(stderr, "Buffer is NULL\n");
        return '\0';
    }
    return buffer[0];
}

// Function to free the buffer
void free_buffer(char* buffer) {
    if (buffer != NULL) {
        free(buffer);
    }
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
        // Call the function to allocate and fill buffer
        char* buffer = allocate_and_fill_buffer(test_data[i]);

        // Check if buffer allocation was successful
        if (buffer != NULL) {
            // Get the first byte of the buffer
            char first_byte = get_first_byte_of_buffer(buffer);

            // Print the first byte of the buffer
            printf("First byte of buffer %d: %c\n", i + 1, first_byte);

            // Free the buffer
            free_buffer(buffer);
        } else {
            fprintf(stderr, "Failed to allocate buffer %d\n", i + 1);
        }
    }

    return 0;
}
