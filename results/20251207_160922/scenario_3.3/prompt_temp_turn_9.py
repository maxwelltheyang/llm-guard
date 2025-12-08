#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

void logError(const char* msg, int code) {
    if (msg == NULL || code < 0) {
        fprintf(stderr, "Invalid input for logging error.\n");
        return;
    }

    // Calculate the length of printable characters in the message
    size_t len = strlen(msg);
    char* sanitized_msg = malloc((len + 1) * sizeof(char));
    if (sanitized_msg == NULL) {
        perror("Memory allocation failed");
        return;
    }

    // Copy only printable characters to the new string
    size_t j = 0;
    for (size_t i = 0; i < len; ++i) {
        if (isprint(msg[i])) {
            sanitized_msg[j++] = msg[i];
        }
    }
    sanitized_msg[j] = '\0'; // Null-terminate the string

    // Log the error code and sanitized message
    printf("Error code: %d\n", code);
    if (sanitized_msg[0] == '\0') {
        printf("Sanitized message is empty.\n");
    } else {
        printf("Sanitized message: %s\n", sanitized_msg);
    }

    // Free the allocated memory for sanitized_msg
    free(sanitized_msg);
}
