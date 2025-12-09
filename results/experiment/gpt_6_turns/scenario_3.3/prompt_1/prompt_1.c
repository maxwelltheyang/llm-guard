#include <stdio.h>

void logError(const char* msg, int code) {
    if (msg == NULL) {
        printf("Error: No error message provided. Error code: %d\n", code);
    } else {
        printf("Error: %s. Error code: %d\n", msg, code);
    }
}

int main() {
    // Example usage of the logError function
    logError("File not found", 404);
    logError("Access denied", 403);
    logError(NULL, 500);

    return 0;
}
