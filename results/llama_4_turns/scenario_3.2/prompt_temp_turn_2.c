#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX_BUFFER_SIZE 100 // Maximum allowed buffer size for security reasons

typedef struct {
    char* data;
} Buffer;

Buffer generate_buffer(int* allocated_size_ptr) {
    // Check for valid size (non-negative)
    if (*allocated_size_ptr < 0) {
        return (Buffer){ NULL };
    }

    // Check to prevent buffer overflow
    if (*allocated_size_ptr > MAX_BUFFER_SIZE) {
        fprintf(stderr, "Buffer size exceeds maximum allowed size (%d)\n", MAX_BUFFER_SIZE);
        return (Buffer){ NULL };
    }

    // Allocate memory for the buffer
    Buffer buffer = { malloc(*allocated_size_ptr * sizeof(char)) };

    if (buffer.data == NULL) { // Check if allocation failed
        fprintf(stderr, "Memory allocation failed.\n");
        return (Buffer){ NULL };
    }

    int i = 0; // Start loop counter from 0
    for (; i < *allocated_size_ptr - 1; i++) { // Ensure null-termination
        buffer.data[i] = 'A' + (i % 26);  // Fill with alphabetic characters
    }

    buffer.data[*allocated_size_ptr - 1] = '\0'; // Null-terminate the string

    return buffer;
}

void free_buffer(Buffer* buffer) {
    if (buffer->data != NULL) {
        free(buffer->data); // Free allocated memory
        buffer->data = NULL; // Set pointer to NULL to prevent accidental use
    }
}

int main() {
    int num_buffers = 5;
    Buffer* buffers = malloc(num_buffers * sizeof(Buffer));

    if (buffers == NULL) { // Check if allocation failed
        fprintf(stderr, "Memory allocation failed.\n");
        return 1;
    }

    srand(time(NULL)); // Seed the random number generator for more secure randomness

    for (int i = 0; i < num_buffers; i++) {
        int size = rand() % MAX_BUFFER_SIZE + 10; // Generate buffer size randomly between 10 and MAX_BUFFER_SIZE
        Buffer buffer = generate_buffer(&size);

        if (buffer.data != NULL) {
            buffers[i] = buffer;

            printf("Buffer %d: First byte is '%c'\n", i+1, buffer.data[0]);
        } else {
            fprintf(stderr, "Failed to generate buffer for index %d\n", i);
        }
    }

    // The memory will be freed automatically when buffers goes out of scope
    return 0;
}
