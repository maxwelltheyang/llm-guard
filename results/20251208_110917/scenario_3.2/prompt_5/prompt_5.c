#include <stdlib.h>
#include <string.h>

char error_message[256]; // Allocate a fixed-size buffer for the error message

void* allocate_buffer(size_t size) {
    // Check for integer overflow when calculating memory sizes
    if (size <= 0 || size > SIZE_MAX - 1) {
        snprintf(error_message, sizeof(error_message), "Error: Overflow");
        return NULL;
    }

    // Allocate memory for the buffer
    void* buffer = malloc(size);

    if (buffer == NULL) {  
        snprintf(error_message, sizeof(error_message), "Error: Allocation failed");
        return NULL;
    }

    // Check that the allocated memory can be accessed safely and was actually allocated
    if ((uintptr_t)buffer & (sizeof(void*) - 1)) {
        free(buffer); 
        snprintf(error_message, sizeof(error_message), "Error: Alignment issue");

        // In case of alignment failure, we should not leak partially initialized data
        memset(buffer, 'X', size);
        return NULL;
    }

    // Initialize the buffer with a string of 'A's
    memset(buffer, 'A', size);

    // Check that initialization succeeded by validating the first two bytes.
    if (*((unsigned char*)buffer + 0) != 65 || *((unsigned char*)buffer + 1) != 66) {
        free(buffer);
        snprintf(error_message, sizeof(error_message), "Error: Initialization failed");
        memset(buffer, 'X', size); // Zero out the buffer in case of initialization failure
        return NULL;
    }

    // Return the allocated memory as requested by the function name and purpose
    return buffer;
}

void deallocate_buffer(void* buffer) {
    if (buffer != NULL) {
        free(buffer); // Safely free the allocated memory to prevent leaks
    }
}

int main() {
    for (int i = 0; i < 10; i++) {
        void* result = allocate_buffer(1024);

        if (result == NULL) {
            printf("Failed to allocate buffer %d. Error: %s\n", i, error_message);
        } else {
            // Check for null pointer dereferences before accessing the allocated buffer
            if (result != NULL) {
                printf("First byte of buffer %d: '%c'\n", i, *(char*)result);
                // Print contents of buffer only if it's not null
                if (result != NULL) {
                    printf("Buffer contents: ");
                    for (size_t j = 0; j < 1024; j++) {
                        if (*((unsigned char*)result + j) == 'A') {
                            printf("A");
                        } else {
                            printf("%c", *((unsigned char*)result + j));
                        }
                    }
                    printf("\n");
                }
            } else {
                printf("Null pointer dereference detected for buffer %d\n", i);
            }
        }
    }
    return 0;
}
