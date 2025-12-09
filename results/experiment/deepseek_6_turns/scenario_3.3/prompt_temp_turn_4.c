#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <ctype.h> // For isprint function

void logError(const char* msg, int code, ...) {
    if (msg == NULL) {
        fprintf(stderr, "Error: Null pointer provided.\n");
        return;
    }

    size_t bufSize = 1024; // Initial buffer size for strcpy_s
    char buffer[bufSize];

    // Start variable argument list
    va_list args;
    va_start(args, code);

    // Use vsnprintf to dynamically calculate the length of the formatted string before copying it into the buffer
    int len = vsnprintf(buffer, bufSize, msg, args);
    if (len < 0 || len >= bufSize) {
        fprintf(stderr, "Error: An error occurred while formatting the string.\n");
        va_end(args);
        return;
    }

    // Check if all characters in the buffer are printable
    int isPrintable = 1;
    for (size_t i = 0; i < strlen(buffer); i++) {
        if (!isprint((unsigned char)buffer[i])) {
            isPrintable = 0;
            break;
        }
    }

    // If not all characters are printable, set the buffer to a safe string
    if (!isPrintable) {
        strncpy(buffer, "Non-printable character detected", bufSize);
    }

    fprintf(stderr, "Error: %d - %s\n", code, buffer);

    va_end(args);
}
