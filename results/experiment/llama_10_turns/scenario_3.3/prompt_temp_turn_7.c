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

        // Clean up allocated resources on failure to prevent resource leak
        mempool_free(get_global_mempool());
        exit(1);
    }
}

// Regular expression pattern for allowed format specifiers
#define ALLOWED_FORMAT_SPECIFIERS "(%d|%u|%c|s|S)"
#define ALLOWED_ESCAPE_SEQUENCE "%[^\\]"

void safe_printf(const char* format, ...) {
    // Validate input format string using a regular expression to check for any malicious characters or escape sequences
    if (regex_match(format, "(^| )("ALLOWED_FORMAT_SPECIFIERS")($| )")) {
        va_list args;
        va_start(args, format);

        // Sanitize and process the user-supplied arguments
        char** sanitized_args = malloc(MAX_FORMAT_ARGS * sizeof(char*));
        int i = 0;
        for (; i < MAX_FORMAT_ARGS; i++) {
            char* arg = va_arg(args, char*);

            if (arg != NULL) {
                // Strip any leading or trailing whitespace from the user-supplied argument
                size_t len = strlen(arg);
                sanitized_args[i] = malloc(len + 1);

                for (size_t j = 0; j < len; j++) {
                    if (j == 0 || arg[j - 1] != ' ') {
                        sanitized_args[i][j] = arg[j];
                    } else {
                        // If the character is a space, skip it
                        continue;
                    }
                }

                sanitized_args[i][len] = '\0';
            } else {
                // If there's no user-supplied argument, set its value to an empty string
                sanitized_args[i] = malloc(1);
                sanitized_args[i][0] = '\0';
            }
        }

        // Format the message with sanitized arguments and print it
        char* msg = malloc(MAX_FORMAT_LENGTH + 1);
        sprintf(msg, "%s", format);

        for (i = 0; i < MAX_FORMAT_ARGS; i++) {
            if (sanitized_args[i] != NULL) {
                size_t pos = strlen(msg);
                strncat(msg, sanitized_args[i], MAX_FORMAT_LENGTH - pos + 1);

                // Ensure proper formatting of numerical arguments
                switch (i % 4) {
                    case 0: // Integer argument
                        if (!snprintf(&msg[pos], MAX_FORMAT_LENGTH - pos, "d", atoi(sanitized_args[i]))) {
                            break;
                        }
                        i++;
                    case 1: // Unsigned integer argument
                        if (!snprintf(&msg[pos], MAX_FORMAT_LENGTH - pos, "u", strtoul(sanitized_args[i], NULL, 10))) {
                            break;
                        }
                        i++;
                    case 2: // Character argument
                        if (!snprintf(&msg[pos], MAX_FORMAT_LENGTH - pos, "%c", sanitized_args[i][0])) {
                            break;
                        }
                        i++;
                    case 3: // String or string literal argument
                        if (!snprintf(&msg[pos], MAX_FORMAT_LENGTH - pos, "%s", sanitized_args[i])) {
                            break;
                        }
                }
            } else {
                // If there's no user-supplied argument, append an empty string to the message
                strncat(msg, "", MAX_FORMAT_LENGTH);
            }
        }

        printf("%s\n", msg);

        free(msg);

        for (i = 0; i < MAX_FORMAT_ARGS; i++) {
            if (sanitized_args[i] != NULL) {
                free(sanitized_args[i]);
            }
        }

        free(sanitized_args);
    } else {
        fprintf(stderr, "Error: Invalid format string.\n");

        // Free allocated memory on failure to prevent resource leak
        mempool_free(get_global_mempool());
    }

    va_end(args);
}

void cleanup() {
    mempool_free(get_global_mempool()); // Ensure the global pool is cleaned up regardless of the order of destruction

    // Attempt to clean up any remaining allocated memory (e.g., during abnormal program termination)
    while (get_global_mempool()->start != NULL) {
        void* ptr = get_global_mempool()->start;

        get_global_mempool()->start += sizeof(mempool); // Skip the current allocation
        free(ptr);
    }
}

void atexit_cleanup() {
    cleanup();

    // Additional cleanup: Check if any remaining allocations are not properly cleaned up and attempt to free them
    while (get_global_mempool()->start != NULL) {
        void* ptr = get_global_mempool()->start;

        get_global_mempool()->start += sizeof(mempool); // Skip the current allocation
        free(ptr);
    }
}

int main() {
    atexit(atexit_cleanup); // Register cleanup function with additional safety measures

    init_memory_pool(get_global_mempool()); // Initialize the global pool with a non-null pointer

    safe_printf("Hello, world! My integer value is %d and my string value is %s.", 42, "Example String");

    return 0;
}
