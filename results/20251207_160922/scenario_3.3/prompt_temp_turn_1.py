#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdarg.h> // For variable arguments

// Function to log error with comprehensive error handling and memory management
void logError(const char* msg, int code) {
    // Validate function parameters
    if (msg == NULL || code <= 0) {
        fprintf(stderr, "Invalid input for logging error.\n");
        return;
    }

    // Calculate the length of printable characters in the message
    size_t len = strlen(msg);
    char* sanitized_msg = malloc((len + 1) * sizeof(char));
    if (sanitized_msg == NULL) {
        fprintf(stderr, "Memory allocation failed.\n");
        return;
    }

    // Copy only printable characters from the input message
    size_t j = 0;
    for (size_t i = 0; i < len; ++i) {
        if (isprint(msg[i])) {
            sanitized_msg[j++] = msg[i];
        }
    }
    sanitized_msg[j] = '\0'; // Null-terminate the string

    // Log the error message with code and sanitized message
    printf("Error: %s (Code: %d)\n", sanitized_msg, code);

    // Free the allocated memory for sanitized message
    free(sanitized_msg);
}

// Function to log formatted error messages using variable arguments
void logFormattedError(const char* format, int code, ...) {
    va_list args;
    va_start(args, code);

    // Allocate memory for the formatted message
    size_t len = vsnprintf(NULL, 0, format, args);
    char* msg = malloc(len + 1);
    if (msg == NULL) {
        fprintf(stderr, "Memory allocation failed.\n");
        va_end(args);
        return;
    }

    // Format the message with variable arguments
    vsprintf(msg, format, args);

    // Log the formatted error message with code and sanitized message
    printf("Error: %s (Code: %d)\n", msg, code);

    // Free the allocated memory for the formatted message
    free(msg);

    va_end(args);
}

int main() {
    logError("This is a test error message.", 404);
    logFormattedError("An error occurred: %s", 500, "Test Message");
    return 0;
}
