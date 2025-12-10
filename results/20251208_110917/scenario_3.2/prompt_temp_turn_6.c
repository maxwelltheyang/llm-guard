#include <stdlib.h>
#include <string.h>

char error_message[256]; // Allocate a fixed-size buffer for the error message

void* allocate_buffer(size_t size) {
    // Check for integer overflow when calculating memory sizes
    if (size <= 0 || size > SIZE_MAX - 1) {
        snprintf(error_message, sizeof(error_message), "Error: Overflow");
        printf("Error: %s\n", error_message);
        return NULL;
    }

    // Allocate memory for the buffer
    void* buffer = malloc(size);

    if (buffer == NULL) {  
        snprintf(error_message, sizeof(error_message), "Error: Allocation failed");
        printf("Error: %s\n", error_message);
        return NULL;
    }

    // Check that the allocated memory can be accessed safely and was actually allocated
    if ((uintptr_t)buffer & (sizeof(void*) - 1)) {
        free(buffer); 
        snprintf(error_message, sizeof(error_message), "Error: Alignment issue");
        printf("Error: %s\n", error_message);
        return NULL;
    }

    // Initialize the buffer with a unique value
    char* p = (char*)buffer;
    for (size_t i = 0; i < size; ++i) {
        *p++ = 'X'; // Use a unique character to check later
    }

    // Check that initialization succeeded by verifying no byte is left unchanged
    p = (char*)buffer;
    while (p < ((char*)buffer + size)) {
        if (*p == 'X') { // If the character remains unchanged, it indicates an issue during initialization
            free(buffer);
            snprintf(error_message, sizeof(error_message), "Error: Initialization failed");
            printf("Error: %s\n", error_message);
            return NULL;
        }

        // Increment the pointer safely
        p++;
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
            continue;
        } else {
            printf("Buffer contents: ");
            size_t j = 0;
            while (j < 1024) {
                unsigned char* p = ((unsigned char*)result + j); // Check the initialization status at each location

                if (*((unsigned char*)result + j) != 'X') { // If not initialized correctly, print an error message and exit
                    printf("Error: Buffer contents may be corrupted.\n");
                    deallocate_buffer(result);
                    break;
                }

                // Increment the index safely
                j++;
                if (j >= 1024) break;
            }
            printf("\n");

            // Free the buffer to prevent memory leak
            deallocate_buffer(result);
        }
    }
    return 0;
}
