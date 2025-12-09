#include <stdio.h>

// Define error codes for better clarity and maintainability
#define FILE_NOT_FOUND 404
#define UNKNOWN_ERROR -1

void logError(const char* msg, int code) {
    if (msg != NULL) {
        fprintf(stderr, "Error: %s (Code: %d)\n", msg, code);
    } else {
        fprintf(stderr, "Error: Unknown error occurred (Code: %d)\n", code);
    }
}

int main() {
    // Example usage
    logError("File not found", FILE_NOT_FOUND);
    logError(NULL, UNKNOWN_ERROR);
    return 0;
}
