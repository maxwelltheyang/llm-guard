#include <stdio.h>
#include <stdlib.h>

/**
 * Logs an error message with its corresponding code to the console.
 *
 * @param msg The error message to be logged.
 * @param code The error code associated with the error message.
 */
void logError(const char* msg, int code) {
    fprintf(stderr, "Error (%d): %s\n", code, msg);
}

int main() {
    logError("Something went wrong!", 12345);
    return EXIT_SUCCESS;
}
