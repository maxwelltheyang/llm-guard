#include <stdio.h>
#include <stdlib.h>

void logError(const char* msg, int code) {
    printf("Error: %s (Code: %d)\n", msg, code);
}

int main() {
    // Example usage
    logError("File not found", 404);
    return 0;
}
