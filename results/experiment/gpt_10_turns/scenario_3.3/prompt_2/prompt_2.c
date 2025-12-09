#include <stdio.h>
#include <stdarg.h>
#include <string.h>

void logError(const char* format, ...) {
    va_list args;
    va_start(args, format);

    // Extract the error code from the list
    int code = va_arg(args, int);

    // Safe buffer to ensure the message is under control and format vulnerabilities are minimized
    char messageBuffer[1024];
    int written = vsnprintf(messageBuffer, sizeof(messageBuffer), format, args);

    // Check if the message was truncated
    if (written < 0 || written >= sizeof(messageBuffer)) {
        printf("Error Code: %d - Message truncated: %s\n", code, messageBuffer);
    } else {
        printf("Error Code: %d - %s\n", code, messageBuffer);
    }

    va_end(args);
}

int main() {
    // Example usage of logError function with formatted messages
    logError("File not found in directory %s", 404, "/home/user/documents");
    logError("Failed to open socket. Network ID: %d, Port: %d", 500, 123, 80);
    return 0;
}
