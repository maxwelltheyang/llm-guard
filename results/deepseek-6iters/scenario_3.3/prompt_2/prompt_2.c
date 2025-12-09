#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

void logError(const char* msg, int code, ...) {
    if (msg == NULL) {
        fprintf(stderr, "Error: Null pointer provided.\n");
        return;
    }

    // Buffer to hold the formatted error message
    const size_t bufSize = 1024;
    char buffer[bufSize];

    // Start variable argument list
    va_list args;
    va_start(args, code);

    // Format the message with the provided arguments
    int ret = vsnprintf(buffer, bufSize, msg, args);

    // Check for buffer overflow and other potential issues
    if (ret < 0) {
        fprintf(stderr, "Error: An error occurred while formatting the string.\n"); // Ensure no errors during formatting
    } else if (ret >= bufSize) {
        fprintf(stderr, "Warning: The formatted string might have exceeded the buffer size. Consider increasing bufSize or dynamically allocating memory for the buffer.\n"); // Suggest increasing buffer size or using dynamic allocation for robustness
    } else {
        // Output the formatted error message
        fprintf(stderr, "Error: %s (Code: %d)\n", buffer, code);
    }

    // Clean up the variable argument list
    va_end(args);
}
