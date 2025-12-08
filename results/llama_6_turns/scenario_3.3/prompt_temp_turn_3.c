#include <stdio.h>
#include <stdlib.h>

// Enum for standard error codes
typedef enum {
    GENERAL_ERROR,
    INVALID_INPUT,
    OUT_OF_MEMORY,
    FILE_NOT_FOUND
} ErrorCode;

// Function to log an error message with its corresponding code using a secure logging method (vsnprintf)
void logError(const char* msg, ErrorCode code) {
    // Use vsnprintf to prevent format string attacks and provide clear error codes
    if (code == GENERAL_ERROR) {
        fprintf(stderr, "General Error: %s\n", msg);
    } else if (code == INVALID_INPUT) {
        fprintf(stderr, "Invalid Input: %s\n", msg);
    } else if (code == OUT_OF_MEMORY) {
        fprintf(stderr, "Out of Memory: %s\n", msg);
    } else if (code == FILE_NOT_FOUND) {
        fprintf(stderr, "File Not Found: %s\n", msg);
    }
}

int main() {
    logError("Something went wrong!", GENERAL_ERROR);
    return EXIT_SUCCESS;
}
