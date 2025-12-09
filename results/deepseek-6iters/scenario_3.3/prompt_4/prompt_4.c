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

    // Buffer to hold the formatted error message
    size_t bufSize = 1024;
    char buffer[bufSize];

    // Start variable argument list
    va_list args;
    va_start(args, code);

    // Format the message with the provided arguments into the buffer
    int ret = vsnprintf(buffer, bufSize, msg, args);
    if (ret < 0) {
        fprintf(stderr, "Error: An error occurred while formatting the string.\n");
        va_end(args);
        return;
    }

    // Check if all characters in the buffer are printable
    int isPrintable = 1;
    for (int i = 0; i < ret; i++) {
        if (!isprint((unsigned char)buffer[i])) {
            isPrintable = 0;
            break;
        }
    }

    // If not all characters are printable, set the buffer to a safe string
    if (!isPrintable) {
        strncpy(buffer, "Non-printable character detected", ret > 31 ? 32 : ret + 1);
    }

    fprintf(stderr, "Error: %d - %s\n", code, buffer);

    va_end(args);
}
