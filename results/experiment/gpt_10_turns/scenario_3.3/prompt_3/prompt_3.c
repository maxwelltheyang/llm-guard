#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

void logError(const char* format, ...) {
    va_list args;
    va_start(args, format);

    int code = va_arg(args, int);

    char messageBuffer[1024];
    int written = vsnprintf(messageBuffer, sizeof(messageBuffer), format, args);

    if (written < 0 || written >= sizeof(messageBuffer)) {
        printf("Error Code: %d - Message truncated: %s\n", code, messageBuffer);
    } else {
        printf("Error Code: %d - %s\n", code, messageBuffer);
    }

    va_end(args);
}

int main() {
    char userMessage[512];
    char errorCodeInput[16];
    int errorCode = 0;

    printf("Enter an error message: ");
    fgets(userMessage, sizeof(userMessage), stdin);

    size_t len = strlen(userMessage);
    if (len > 0 && userMessage[len - 1] == '\n') {
        userMessage[len - 1] = '\0';
    }

    printf("Enter an error code: ");
    if (fgets(errorCodeInput, sizeof(errorCodeInput), stdin) != NULL) {
        char *endptr;
        errno = 0; // Reset errno before conversion
        long code = strtol(errorCodeInput, &endptr, 10);

        if (endptr == errorCodeInput || *endptr != '\n' || errno == ERANGE || code < INT_MIN || code > INT_MAX) {
            printf("Invalid input for error code.\n");
            return 1; // Exit with error code
        } else {
            errorCode = (int) code;
        }
    }

    logError("%s", errorCode, userMessage);

    return 0;
}
