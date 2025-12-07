#include <stdio.h>

void logError(const char* msg, int code) {
    printf("Error: %s (Code: %d)\n", msg, code);
}
