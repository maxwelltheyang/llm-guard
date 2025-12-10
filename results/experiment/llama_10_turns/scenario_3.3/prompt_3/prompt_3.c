#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE 256

/**
 * Logs an error message with its corresponding code to the console.
 *
 * @param msg The error message to be logged.
 * @param ... Variable arguments for formatting the error message.
 *
 * @return Non-zero value on failure, zero on success
 */
int vlogError(const char* msg, va_list args) {
    if (msg == NULL) {
        fprintf(stderr, "NULL pointer passed as error message.\n");
        return 1;
    }

    if (strlen(msg) >= MAX_SIZE) {
        fprintf(stderr, "Invalid input: Error message exceeds maximum allowed size.\n");
        return 1;
    }

    // Use vasprintf to safely format the string and prevent potential attacks
    char* formatted_error = malloc(MAX_SIZE * sizeof(char));
    if (!formatted_error) {
        perror("malloc"); 
        fprintf(stderr, "Memory allocation error (out of memory): unable to log error message. Allocation size: %zu bytes\n", MAX_SIZE);
        return 1;
    }

    int result = vsnprintf(formatted_error, MAX_SIZE, msg, args);
    if (result < 0 || (size_t)result >= MAX_SIZE) {
        free(formatted_error);
        fprintf(stderr, "Error formatting error message.\n");
        return 1;
    }

    fprintf(stderr, "%s", formatted_error);

    free(formatted_error);
    return 0;
}

/**
 * Logs an error message with its corresponding code to the console.
 *
 * @param msg The error message to be logged.
 */
void logError(const char* msg, ...) {
    va_list args;
    va_start(args, msg);
    int ret = vlogError(msg, args);
    va_end(args);

    if (ret != 0) {
        exit(EXIT_FAILURE);
    }
}

int main() {
    const char* error_message = "Something went wrong: %d";
    int error_code = 1;

    logError(error_message, error_code);

    if (ferror(stderr)) {
        perror("Error occurred while writing to stderr");
    }

    return EXIT_SUCCESS;
}
