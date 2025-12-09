#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>  // For exit()

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
    char userMessage[256];
    char errorCodeInput[256];
    int errorCode;

    // Example usage for predefined messages
    logError("File not found (Code: %d)", FILE_NOT_FOUND);
    logError("Unknown error occurred (Code: %d)", UNKNOWN_ERROR);

    // Allow user to input a custom error message
    printf("Enter a custom error message: ");
    fgets(userMessage, sizeof(userMessage), stdin);
    userMessage[strcspn(userMessage, "\n")] = '\0';  // Remove trailing newline

    printf("Enter an error code: ");
    fgets(errorCodeInput, sizeof(errorCodeInput), stdin);

    // Use sscanf to safely convert string to integer and check if it was successful
    if (sscanf(errorCodeInput, "%d", &errorCode) != 1) {
        fprintf(stderr, "Invalid input. Please enter a valid integer for the error code.\n");
        exit(EXIT_FAILURE);
    }

    // Log the user-provided message and error code
    logError("%s (Code: %d)", userMessage, errorCode);

    return 0;
}
