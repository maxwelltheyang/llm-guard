#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

#define MAX_ALLOC_SIZE (1024 * 1024) // 1MB
#define MINIMAL_MALLOC_SIZE 128
#define FORMAT_STRING_MAX_LENGTH 256
#define INITIAL_POOL_SIZE MAX_ALLOC_SIZE

typedef struct {
    void* start;
    size_t size;
} mempool;

int init_mempool(mempool* mp, size_t size) {
    if (size == 0 || !mp) return -1; // Return an error code to indicate pool initialization failure

    // Calculate memory requirements using a safer approach to avoid integer overflow
    void* addr = malloc(size);
    if (!addr) {
        fprintf(stderr, "Error: Unable to allocate memory for the pool.\n");
        return -1;
    }

    mp->start = addr;
    mp->size = size;
    return 0;
}

void mempool_free(mempool* mp) {
    if (mp && mp->start) free(mp->start);
    // Reset the memory pool struct
    mp->start = NULL;
}

mempool* get_global_mempool() {
    static mempool global_mempool = {NULL, 0};
    return &global_mempool;
}

void init_memory_pool(mempool* mp) {
    if (!mp || !init_mempool(mp, INITIAL_POOL_SIZE)) {
        fprintf(stderr, "Error initializing the memory pool.\n");
        exit(1);
    }
}

void safe_printf(const char* format, ...) {
    // Validate input format string
    for (size_t i = 0; format[i] != '\0'; ++i) {
        if ((format[i] == '%' && format[i + 1] == 'n') || (format[i] == '%' && format[i + 1] == '%')) {
            fprintf(stderr, "Error: Invalid format string.\n");
            return;
        }
    }

    // Allocate enough space for the formatted message
    size_t msg_size = FORMAT_STRING_MAX_LENGTH;
    void* msg = mempool_alloc(get_global_mempool(), msg_size);

    if (msg) {
        va_list args;
        int written_bytes = vsnprintf(msg, msg_size - 1, format, args); // Ensure null-termination of the message string

        if (written_bytes < 0 || written_bytes >= msg_size) { // Handle potential buffer overflows
            fprintf(stderr, "Error: Failed to write formatted message.\n");

            // Free allocated memory on failure to prevent resource leak
            free(msg);
            return;
        }

        // Print the formatted message
        printf("%s\n", msg);

        free(msg); // Free allocated memory after printing to prevent memory leaks
    } else {
        fprintf(stderr, "Error: Failed to allocate memory for printing.\n");

        // Clean up allocated resources on failure to prevent resource leak
        mempool_free(get_global_mempool());
    }
}

void cleanup() {
    mempool_free(get_global_mempool());
}

int main() {
    atexit(cleanup); // Register cleanup function

    init_memory_pool(get_global_mempool()); // Initialize the global pool with a non-null pointer

    safe_printf("Hello, world! My integer value is %d.", 42);

    return 0;
}
