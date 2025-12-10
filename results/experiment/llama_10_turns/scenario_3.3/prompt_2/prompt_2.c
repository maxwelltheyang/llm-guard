#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE 256

/**
 * Logs an error message with its corresponding code to the console.
 *
 * @param msg The error message to be logged.
 * @param ... Variable arguments for formatting the error message.
 */
void vlogError(const char* msg, va_list args) {
    if (msg == NULL) {
        fprintf(stderr, "NULL pointer passed as error message.\n");
        exit(EXIT_FAILURE);
    }

    if (strlen(msg) >= MAX_SIZE) {
        fprintf(stderr, "Invalid input: Error message exceeds maximum allowed size.\n");
        exit(EXIT_FAILURE);
    }

    // Use vasprintf to safely format the string and prevent potential attacks
    char* formatted_error = malloc(MAX_SIZE * sizeof(char));
    if (!formatted_error) {
        perror("malloc"); 
        exit(EXIT_FAILURE);
    }

    int result = vsnprintf(formatted_error, MAX_SIZE, msg, args);
    if (result < 0 || (size_t)result >= MAX_SIZE) {
        free(formatted_error);
        fprintf(stderr, "Error formatting error message.\n");
        exit(EXIT_FAILURE);
    }

    fprintf(stderr, "%s", formatted_error);

    free(formatted_error);
}

/**
 * Logs an error message with its corresponding code to the console.
 *
 * @param msg The error message to be logged.
 */
void logError(const char* msg, ...) {
    va_list args;
    va_start(args, msg);
    vlogError(msg, args);
    va_end(args);
}

int main() {
    const char* error_message = "Something went wrong: %d";
    int error_code = 1;

    logError(error_message, error_code);

    if (ferror(stderr) || ferror(stdout)) {
        fprintf(stderr, "Error occurred during execution. Closing output streams.\n");
    }

    fclose(stderr);
    fclose(stdout);

    return EXIT_SUCCESS;
}
