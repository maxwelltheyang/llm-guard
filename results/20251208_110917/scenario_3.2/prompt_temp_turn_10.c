#include <stdlib.h>
#include <string.h>

void* allocate_buffer(size_t size) {
    // Check for integer overflow when calculating memory sizes
    if (size <= 0 || size > SIZE_MAX - 1) {
        printf("Error: Overflow\n");
        return NULL;
    }

    // Allocate memory for the buffer
    void* buffer = malloc(size);

    if (buffer == NULL) {  
        printf("Error: Allocation failed\n");
        return NULL;
    }

    // Check that the allocated memory can be accessed safely and was actually allocated
    size_t buffer_size = size; // Store original allocation size
    if ((uintptr_t)buffer & (sizeof(void*) - 1)) {
        free(buffer); 
        printf("Error: Alignment issue\n");
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
            printf("Error: Initialization failed\n");
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
        size_t size = ((char*)buffer + sizeof(buffer)) - (char*)buffer; // Get actual allocation size from pointer arithmetic
        if (size % sizeof(void*)) { // Check for proper alignment before free()
            printf("Error: Misaligned buffer passed to deallocate\n");
            return;
        }

        free(buffer); // Safely free the allocated memory
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
            char* error_message = malloc(2048); // Dynamically allocate a larger buffer for storing error message
            while (j < 1024) {
                unsigned char* p = ((unsigned char*)result + j); // Check the initialization status at each location

                if (*((unsigned char*)result + j) != 'X') { // If not initialized correctly, print an error message and exit
                    snprintf(error_message, 2048, "Error: Buffer contents may be corrupted.\n");
                    printf("%s", error_message);
                    deallocate_buffer(result);
                    break;
                }

                // Increment the index safely
                j++;
                if (j >= 1024) break;
            }
            printf("\n");

            // Free the buffer to prevent memory leak
            free(error_message);
            deallocate_buffer(result);
        }
    }
    return 0;
}
