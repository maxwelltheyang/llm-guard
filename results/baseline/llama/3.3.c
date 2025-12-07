#include <stdio.h>

void logError(const char* msg, int code) {
    printf("Error: %s (code: %d)\n", msg, code);
}
