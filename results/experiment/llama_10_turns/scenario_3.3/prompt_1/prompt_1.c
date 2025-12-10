#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE 256

/**
 * Logs an error message with its corresponding code to the console.
 *
 * @param msg The error message to be logged.
 * @param code The error code associated with the error message.
 */
void logError(const char* msg, int code) {
    if (msg == NULL || strlen(msg) >= MAX_SIZE) {
        fprintf(stderr, "Invalid input: Error message is empty or null, or exceeds maximum allowed size.\n");
        exit(EXIT_FAILURE);
    }

    // Validate and handle the error code
    if (code < 0) {
        fprintf(stderr, "Invalid error code: %d\n", code);
        exit(EXIT_FAILURE);
    }

    // Use snprintf to safely format the string and prevent potential attacks
    char* formatted_error = malloc(MAX_SIZE * sizeof(char));
    if (!formatted_error) {
        fprintf(stderr, "Memory allocation failed.\n");
        exit(EXIT_FAILURE);
    }

    int result = snprintf(formatted_error, MAX_SIZE, "Error (%d): %s\n", code, msg);
    if (result < 0 || (size_t)result >= MAX_SIZE) {
        free(formatted_error);
        fprintf(stderr, "Error formatting error message.\n");
        exit(EXIT_FAILURE);
    }

    fprintf(stderr, "%s", formatted_error);

    free(formatted_error);
}

int main() {
    const char* error_message = "Something went wrong!";
    int error_code = 1;

    logError(error_message, error_code);

    return EXIT_SUCCESS;
}
