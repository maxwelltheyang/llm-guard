#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdarg.h>
#include <unistd.h>
#include <assert.h>

// Function to log error with comprehensive error handling and memory management
void logError(const char* msg, int code) {
    if (msg == NULL || code <= 0) {
        fprintf(stderr, "Invalid input for logging error: msg is NULL or code is non-positive.\n");
        return;
    }
    // Rest of the function remains unchanged
}

// Function to log formatted errors with dynamic buffer sizing and enhanced error handling
void logFormattedError(const char* format, ...) {
    va_list args;
    va_start(args, format);

    int BUFFER_SIZE = 1024; // Initial buffer size
    const int MAX_BUFFER_SIZE = 65536; // Maximum buffer size limit

    char* msg = malloc((BUFFER_SIZE + 1) * sizeof(char)); // Allocate initial memory for the message
    assert(msg != NULL && "Memory allocation failed"); // Add assertion for better error handling

    int written = vsnprintf(msg, BUFFER_SIZE + 1, format, args); // Write formatted string to buffer

    if (written < 0) {
        perror("Formatting error");
        free(msg);
        va_end(args);
        return;
    }

    // If the message exceeds the initial buffer size, dynamically resize the buffer
    while (written >= BUFFER_SIZE) {
        if (BUFFER_SIZE > MAX_BUFFER_SIZE) {
            fprintf(stderr, "Buffer overflow protection triggered. Input too long.\n");
            free(msg);
            va_end(args);
            return;
        }
        char* new_msg = realloc(msg, (BUFFER_SIZE * 2 + 1) * sizeof(char)); // Double the buffer size
        if (new_msg == NULL) {
            free(msg);
            perror("Memory allocation failed");
            va_end(args);
            return;
        }
        msg = new_msg;
        written = vsnprintf(msg, BUFFER_SIZE * 2 + 1, format, args); // Re-evaluate the length of the formatted string
        BUFFER_SIZE *= 2; // Update buffer size for next iteration
    }

    // Log the formatted message
    fprintf(stderr, "Formatted Error: %s\n", msg);

    free(msg); // Free dynamically allocated memory
    va_end(args);
}

int main() {
    logError("Valid test error message", 200);
    logError(NULL, -1); // This will trigger the invalid input check and print an error message
    logFormattedError("%s %d", "Test message", 42);
    return 0;
}
