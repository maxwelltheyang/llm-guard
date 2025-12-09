#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdarg.h>
#include <unistd.h>

// Function to log error with comprehensive error handling and memory management
void logError(const char* msg, int code) {
    if (msg == NULL || code <= 0) {
        fprintf(stderr, "Invalid input for logging error: msg is NULL or code is non-positive.\n");
        return;
    }

    size_t len = strlen(msg);
    char* sanitized_msg = malloc((len + 1) * sizeof(char));
    if (sanitized_msg == NULL) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }

    size_t j = 0;
    for (size_t i = 0; i < len; i++) {
        if (isprint(msg[i])) {
            sanitized_msg[j++] = msg[i];
        }
    }
    sanitized_msg[j] = '\0';

    // Log the error message with code
    fprintf(stderr, "Error: %s\nCode: %d\n", sanitized_msg, code);

    // Free allocated memory
    free(sanitized_msg);
}

// Function to log formatted error messages with better error handling for allocation failures
void logFormattedError(const char* format, ...) {
    int BUFFER_SIZE = 1024;
    char msg[BUFFER_SIZE]; // Use a fixed-size array instead of dynamically allocated memory

    va_list args;
    va_start(args, format);
    int num_chars = vsnprintf(msg, sizeof(msg), format, args);
    if (num_chars < 0) {
        perror("Formatting error");
        return;
    }

    // Log the formatted message
    fprintf(stderr, "Error: %s\n", msg);

    va_end(args);
}

int main() {
    // Test logError function with valid input
    logError("Valid test error message", 200);

    // Test logError function with invalid input
    logError(NULL, -1);

    // Test logFormattedError function
    logFormattedError("Test formatted error message with code: %d", 200);

    return 0;
}
