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

// Function to log formatted error messages safely using dynamic memory allocation
void logFormattedError(const char* format, ...) {
    va_list args;
    va_start(args, format);

    int BUFFER_SIZE = 1024; // Define a default buffer size
    char* msg = malloc((BUFFER_SIZE + 1) * sizeof(char)); // Allocate dynamic memory for the message

    if (msg == NULL) {
        perror("Memory allocation failed");
        va_end(args);
        return;
    }

    int written = vsnprintf(msg, BUFFER_SIZE + 1, format, args); // Write formatted string to buffer

    if (written < 0) {
        perror("Formatting error");
        free(msg);
        va_end(args);
        return;
    } else if (written >= BUFFER_SIZE) {
        fprintf(stderr, "Error: The formatted message exceeds the buffer size.\n");
        free(msg);
        va_end(args);
        return;
    }

    // Log the formatted message
    fprintf(stderr, "Formatted Error: %s\n", msg);

    free(msg); // Free dynamically allocated memory
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
