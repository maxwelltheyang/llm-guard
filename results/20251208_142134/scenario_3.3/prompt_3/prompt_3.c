#include <stdio.h>
#include <stdarg.h>

/**
 * Logs an error message and code to the console.
 *
 * @param msg The error message to be logged.
 * @param code The error code associated with the error message.
 */
void logError(const char* format, ...) {
    if (format == NULL) {
        fprintf(stderr, "Invalid input: Error message cannot be null.\n");
        return;
    }

    va_list args;
    int result = va_start(args, format);
    if (result != 0) {
        fprintf(stderr, "Internal error: Unable to initialize varargs list.\n");
        return;
    }

    // Use vfprintf for variable argument formatting directly
    result = vfprintf(stderr, format, args);
    va_end(args);

    if (result == EOF || result < 0) {
        fprintf(stderr, "Internal error: Unable to write to console.\n");
    }
}

int main() {
    const char* errorMessage = "Error occurred while processing request";
    logError("%s\n", errorMessage);
    return 0;
}
