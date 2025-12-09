#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <stdlib.h>  // For exit()

// Define error codes for better clarity and maintainability
#define FILE_NOT_FOUND 404
#define UNKNOWN_ERROR -1

void logError(const char* baseMessage, const char* userMessage, int value, int code) {
    fprintf(stderr, "Error: %s - %s (Value: %d, Code: %d)\n", baseMessage, userMessage, value, code);
}

int main() {
    char userMessage[256];
    char errorCodeInput[256];
    int errorCode;
    char additionalValueInput[256];
    int additionalValue;

    // Example usage for predefined messages
    logError("File operation failed", "File not found", 0, FILE_NOT_FOUND);
    logError("System warning", "Unknown error occurred", 0, UNKNOWN_ERROR);

    // Allow user to input a custom error message
    printf("Enter a custom error message: ");
    if (fgets(userMessage, sizeof(userMessage), stdin) != NULL) {
        userMessage[strcspn(userMessage, "\n")] = '\0';  // Remove trailing newline
    } else {
        fprintf(stderr, "Error reading input.\n");
        exit(EXIT_FAILURE);
    }

    // Ask the user for an additional integer
    printf("Enter an additional integer value: ");
    if (fgets(additionalValueInput, sizeof(additionalValueInput), stdin) != NULL) {
        if (sscanf(additionalValueInput, "%d", &additionalValue) != 1) {
            fprintf(stderr, "Invalid input. Please enter a valid integer.\n");
            exit(EXIT_FAILURE);
        }
    } else {
        fprintf(stderr, "Error reading input.\n");
        exit(EXIT_FAILURE);
    }

    printf("Enter an error code: ");
    if (fgets(errorCodeInput, sizeof(errorCodeInput), stdin) != NULL) {
        // Use sscanf to safely convert string to integer and check if it was successful
        if (sscanf(errorCodeInput, "%d", &errorCode) != 1) {
            fprintf(stderr, "Invalid input. Please enter a valid integer for the error code.\n");
            exit(EXIT_FAILURE);
        }
    } else {
        fprintf(stderr, "Error reading input.\n");
        exit(EXIT_FAILURE);
    }

    // Log the user-provided message, additional value, and error code
    logError("Custom user message", userMessage, additionalValue, errorCode);

    return 0;
}
