#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>

void logError(const char* msg, int code, ...) {
    va_list args;
    va_start(args, code);

    printf("Error: %s (Code: %d) - ", msg, code);

    // Safely format the additional information if needed
    const char *additionalInfo = va_arg(args, const char *);
    if (additionalInfo != NULL) {
        printf("%s", additionalInfo);
    }

    printf("\n");
    va_end(args);
}

int main() {
    logError("File not found", 404, "Additional info: file does not exist");
    return 0;
}
