#include <stdio.h>
#include <stdarg.h>

void logError(const char* format, ...) {
    va_list args;
    va_start(args, format);

    // Print the formatted error message
    printf("Error: ");
    vprintf(format, args);

    va_end(args);
}

int main() {
    // Example usage of the logError function with formatted messages
    logError("File not found. Error code: %d\n", 404);
    logError("Access denied for user: %s. Error code: %d\n", "admin", 403);
    logError("Unknown error. Error code: %d\n", 500);

    return 0;
}
