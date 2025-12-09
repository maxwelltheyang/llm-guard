#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void logError(const char* msg, int code) {
    if (msg == NULL) {
        fprintf(stderr, "Error: Null pointer provided.\n");
        return;
    }
    const size_t bufSize = 1024; // Adjust based on expected message length
    char buffer[bufSize];
    snprintf(buffer, bufSize, "Error: %s (Code: %d)\n", msg, code);
    if (strlen(msg) >= bufSize - strlen("Error: ") - strlen(" (Code: X)\n") - 1) {
        fprintf(stderr, "Error: Message too long.\n");
    } else {
        fprintf(stderr, "%s", buffer);
    }
}
