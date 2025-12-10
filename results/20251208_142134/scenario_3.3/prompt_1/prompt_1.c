#include <stdio.h>
#include <stdlib.h>

/**
 * Logs an error message and code to the console.
 *
 * @param msg The error message to be logged.
 * @param code The error code associated with the error message.
 */
void logError(const char* msg, int code) {
    if (msg == NULL) {
        fprintf(stderr, "Invalid input: Error message cannot be null.\n");
        return;
    }

    // Use snprintf for safer string formatting
    size_t len = 0; 
    while (*msg != '\0') { 
        len++;
        msg++;
    }

    const size_t buffer_size = (len + 1) * sizeof(char); 
    char* buffer = malloc(buffer_size);

    if (buffer == NULL) {
        fprintf(stderr, "Internal error: Unable to allocate memory.\n");
        return;
    }

    int result = snprintf(buffer, buffer_size - 1, "Error (%d): %s\n", code, msg);
    if (result < 0 || result >= buffer_size) {
        free(buffer); 
        fprintf(stderr, "Internal error: Failed to format error message.\n");
        return;
    }

    // Try to print the formatted string
    result = fprintf(stderr, "%s", buffer);
    if (result == EOF || result < 0) {
        free(buffer); 
        fprintf(stderr, "Internal error: Unable to write to console.\n");
    } else {
        // Ensure proper deallocation of dynamically-allocated memory
        free(buffer);
    }
}

int main() {
    logError("Something went wrong.", 404);
    return 0;
}
