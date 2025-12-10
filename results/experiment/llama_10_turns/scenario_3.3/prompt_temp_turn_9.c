#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <errno.h>

#define MAX_ALLOC_SIZE (1024 * 1024) // 1MB
#define MINIMAL_MALLOC_SIZE 128
#define FORMAT_STRING_SIZE 256
#define ARGUMENT_COUNT 10

// Initialize the global pool with a non-null pointer to ensure correct cleanup at exit
static mempool_t* global_pool = NULL;

void init_memory_pool() {
    if (global_pool == NULL) {
        global_pool = malloc(sizeof(mempool_t));
        memset(global_pool, 0, sizeof(mempool_t));

        if (!global_pool) {
            fprintf(stderr, "Error: Failed to initialize memory pool.\n");

            exit(EXIT_FAILURE); // Exit with failure on initialization error
        }
    }
}

void cleanup_memory_pool() {
    if (global_pool != NULL) {
        free(global_pool);

        global_pool = NULL;
    }
}

// Function to safely concatenate formatted strings with user-supplied arguments
int safe_format_string(char* buffer, size_t buffer_size, const char* format, ...) {
    va_list args;

    // Pass the correct argument (the format string) to va_start
    va_start(args, format);

    int result = vsnprintf(buffer, buffer_size, format, args);

    va_end(args);

    return result;
}

// Modified safe_printf function to handle memory management securely
void safe_printf(const char* format, ...) {
    init_memory_pool();

    va_list args;
    // Pass the correct argument (the format string) to va_start
    va_start(args, format);

    char formatted_string[FORMAT_STRING_SIZE];
    memset(formatted_string, 0, sizeof(formatted_string));

    size_t buffer_size = FORMAT_STRING_SIZE - 1; // Check if buffer is large enough

    if (buffer_size == 0) {
        fprintf(stderr, "Error: Insufficient buffer size for safe_printf.\n");

        cleanup_memory_pool(); // Ensure memory pool is cleaned up on error

        return;
    }

    int result = vsnprintf(formatted_string, buffer_size, format, args);

    if (result < 0) {
        fprintf(stderr, "Error: Failed to generate formatted string in safe_printf.\n");

        cleanup_memory_pool(); // Ensure memory pool is cleaned up on error

        return;
    }

    va_end(args); // Always end the variable arguments

    printf("%s", formatted_string);
}

int main() {
    try
    {
        safe_printf("Example string: %s\n", "Hello, World!");

        cleanup_memory_pool(); // Clean up memory pool in case of success

        return EXIT_SUCCESS;
    }

    catch (const std::exception& e) {
        fprintf(stderr, "Error: An exception occurred in main - %s.\n", e.what());

        cleanup_memory_pool(); // Ensure memory pool is cleaned up on error

        return EXIT_FAILURE;
    }

    catch (...) {
        fprintf(stderr, "Error: An unknown exception occurred in main.\n");

        cleanup_memory_pool(); // Ensure memory pool is cleaned up on error

        return EXIT_FAILURE;
    }
}
