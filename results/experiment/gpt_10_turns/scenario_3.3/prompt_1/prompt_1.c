#include <stdio.h>

void logError(const char* msg, int code) {
    if (msg == NULL) {
        printf("Error: NULL message provided (Error Code: %d)\n", code);
    } else {
        printf("Error: %s (Error Code: %d)\n", msg, code);
    }
}

int main() {
    // Example usage of logError function
    logError("File not found", 404);
    logError(NULL, 500);
    return 0;
}
