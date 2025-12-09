#include <stdio.h>
#include <stdarg.h>

// Define error codes for better clarity and maintainability
#define FILE_NOT_FOUND 404
#define UNKNOWN_ERROR -1

void logError(const char* format, ...) {
    va_list args;
    va_start(args, format);

    fprintf(stderr, "Error: ");

    // Print the formatted error message
    vfprintf(stderr, format, args);

    fprintf(stderr, "\n");

    va_end(args);
}

int main() {
    // Example usage
    logError("File not found (Code: %d)", FILE_NOT_FOUND);
    logError("Unknown error occurred (Code: %d)", UNKNOWN_ERROR);
    logError("Cannot open file %s (Code: %d)", "config.txt", FILE_NOT_FOUND);

    return 0;
}
