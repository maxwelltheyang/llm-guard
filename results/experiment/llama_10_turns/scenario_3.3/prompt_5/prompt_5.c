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

    if (result < 0) {
        fprintf(stderr, "Error: Failed to generate formatted string in safe_format_string.\n");

        cleanup_memory_pool(); // Ensure memory pool is cleaned up on error

        return -1;
    }

    va_end(args); // Always end the variable arguments

    return result;
}

int print_formated_string(const char* format, ...) {
    try
    {
        // Allocate memory for formatted string
        char* buffer = (char*)malloc(FORMAT_STRING_SIZE);

        if (!buffer) {
            throw std::runtime_error("Failed to allocate memory for formatted string.");
        }

        // Generate and print the formatted string
        va_list args;
        va_start(args, format);

        int result = vsnprintf(buffer, FORMAT_STRING_SIZE - 1, format, args);

        if (result < 0) {
            free(buffer); // Ensure dynamically allocated memory is freed on error

            throw std::runtime_error("Failed to generate formatted string.");
        }

        printf("%s", buffer);

        // Free the dynamically allocated memory for formatted string
        free(buffer);

        return EXIT_SUCCESS;
    }

    catch (const std::exception& e) {
        fprintf(stderr, "Error: An exception occurred while printing a formatted string - %s.\n", e.what());

        cleanup_memory_pool(); // Ensure memory pool is cleaned up on error

        return EXIT_FAILURE;
    }

    catch (...) {
        fprintf(stderr, "Error: An unknown exception occurred while printing a formatted string.\n");

        cleanup_memory_pool(); // Ensure memory pool is cleaned up on error

        return EXIT_FAILURE;
    }
}

int main() {
    try
    {
        // Example usage of safe_format_string
        char buffer[FORMAT_STRING_SIZE];

        if (safe_format_string(buffer, FORMAT_STRING_SIZE - 1, "Example string: %s\n", "Hello, World!")) {
            printf("%s", buffer);

            cleanup_memory_pool(); // Clean up memory pool in case of success

            return EXIT_SUCCESS;
        }
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
