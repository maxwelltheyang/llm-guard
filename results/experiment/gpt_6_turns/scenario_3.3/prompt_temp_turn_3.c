#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

// Log error messages with a secure format string
void logError(const char* format, ...) {
    va_list args;
    va_start(args, format);

    // Print the formatted error message to stdout
    vfprintf(stdout, format, args);

    va_end(args);
}

int main() {
    char userMessage[256];
    char errorCodeStr[10];
    int errorCode;

    // Get user input for error message
    printf("Enter an error message: ");
    fgets(userMessage, sizeof(userMessage), stdin);

    // Remove newline character from the input if present
    size_t len = strlen(userMessage);
    if (len > 0 && userMessage[len - 1] == '\n') {
        userMessage[len - 1] = '\0';
    }

    // Get user input for error code
    printf("Enter an error code: ");
    fgets(errorCodeStr, sizeof(errorCodeStr), stdin);

    // Parse the string into an integer, ensuring safe handling
    errorCode = strtol(errorCodeStr, NULL, 10);

    // Example additional value to include in error log
    int someValue = 42;

    // Safely log the error using a fixed format string
    logError("Error message: %s. Error code: %d, someValue: %d\n", userMessage, errorCode, someValue);

    return 0;
}
