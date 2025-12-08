#include <stdio.h>

void logError(const char* msg, int code) {
    fprintf(stderr, "Error: %s (Code: %d)\n", msg, code);
}
