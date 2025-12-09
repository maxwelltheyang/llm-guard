#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdarg.h> // For variable arguments
#include <unistd.h>  // For read and write system calls (Unix-like systems)

// Function to log error with comprehensive error handling and memory management
void logError(const char* msg, int code) {
    if (msg == NULL || code <= 0) {
        fprintf(stderr, "Invalid input for logging error.\n");
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

    // Log the error message with its code
    fprintf(stderr, "Error: %s\n", sanitized_msg);
    free(sanitized_msg);
}

// Function to log an error with a formatted message using variable arguments
void logFormattedError(const char* fmt, ...) {
    va_list args;
    va_start(args, fmt);

    // Allocate buffer for the formatted string
    size_t bufsize = 1024;
    char* buf = malloc(bufsize * sizeof(char));
    if (buf == NULL) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }

    // Format the string with variable arguments
    int len = vsnprintf(buf, bufsize, fmt, args);
    va_end(args);

    if (len < 0) {
        free(buf);
        perror("Buffer overflow");
        exit(EXIT_FAILURE);
    }

    // Ensure the buffer is null-terminated
    buf[len] = '\0';

    // Log the formatted error message
    fprintf(stderr, "Error: %s\n", buf);
    free(buf);
}

int main() {
    logError("Hello, World!", 404);
    logFormattedError("An error occurred with code %d", 500);
    return 0;
}
