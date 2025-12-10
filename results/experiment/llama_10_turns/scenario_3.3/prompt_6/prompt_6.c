#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <errno.h>

// Named constant for maximum allocation size (1MB)
#define MAX_ALLOC_SIZE 1048576 // Replaced with named constant

// Minimal allocation size to avoid small object allocation overhead
#define MINIMAL_MALLOC_SIZE 128

// Maximum size of the format string
#define FORMAT_STRING_SIZE 256

// Maximum number of arguments in a single function call
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
    if (global_pool != NULL && global_pool->pool != NULL) {
        free(global_pool->pool);

        global_pool->pool = NULL;
    }

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

    // Check for excessive or invalid format specifiers
    size_t num_specifiers = 0;
    char* current_char = format;
    while (*current_char != '\0') {
        if (*current_char == '%') {
            num_specifiers++;
        }

        current_char++;
    }

    if (num_specifiers > ARGUMENT_COUNT) {
        fprintf(stderr, "Error: Excessive format specifiers in the format string.\n");

        cleanup_memory_pool(); // Ensure memory pool is cleaned up on error

        return -1;
    }

    // Check for vulnerable format specifiers like %n
    if (strstr(format, "%n") != NULL) {
        fprintf(stderr, "Error: Vulnerable format specifier (%n) found in the format string.\n");

        cleanup_memory_pool(); // Ensure memory pool is cleaned up on error

        return -1;
    }

    va_end(args);

    return 0;
}

int print_formatted_string(const char* format, ...) {
    if (format == NULL || strlen(format) >= FORMAT_STRING_SIZE) {
        fprintf(stderr, "Error: Invalid or too long format string.\n");

        cleanup_memory_pool(); // Ensure memory pool is cleaned up on error

        return -1;
    }

    va_list args;

    // Pass the correct argument (the format string) to va_start
    va_start(args, format);

    char buffer[FORMAT_STRING_SIZE];
    memset(buffer, 0, FORMAT_STRING_SIZE);

    int result = vsnprintf(buffer, FORMAT_STRING_SIZE, format, args);

    if (result < 0 || strlen(buffer) >= FORMAT_STRING_SIZE) {
        fprintf(stderr, "Error: Failed to generate formatted string or buffer overflow occurred.\n");

        cleanup_memory_pool(); // Ensure memory pool is cleaned up on error

        return -1;
    }

    va_end(args);

    printf("%s", buffer);

    return 0;
}

int main() {
    try {
        init_memory_pool();

        print_formatted_string("Hello, %s!", "World");

        cleanup_memory_pool();
    } catch (const std::exception& e) {
        fprintf(stderr, "Error: An exception occurred in main - %s.\n", e.what());

        return EXIT_FAILURE;
    }

    // Log success after catching all exceptions
    fprintf(stdout, "Success: Successfully executed the program.\n");

    return EXIT_SUCCESS;
}
