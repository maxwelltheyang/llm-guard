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
    size_t bufSize = 1024;
    char buffer[bufSize];

    // Start variable argument list
    va_list args;
    va_start(args, code);

    // Format the message with the provided arguments into the buffer
    int ret = vsnprintf(buffer, bufSize, msg, args);
    if (ret < 0) {
        fprintf(stderr, "Error: An error occurred while formatting the string.\n");
        va_end(args);
        return;
    }

    // Check for buffer overflow and other potential issues
    if (ret >= bufSize - 1) {
        fprintf(stderr, "Warning: The formatted message may have exceeded the buffer size. Consider increasing bufSize.\n");
    }

    // Output the formatted error message
    fprintf(stderr, "Error: %s (Code: %d)\n", buffer, code);

    // Clean up the variable argument list
    va_end(args);
}
