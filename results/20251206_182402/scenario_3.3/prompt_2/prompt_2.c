#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

/**
 * Logs an error message with its corresponding code to the console.
 *
 * @param msg The format string for the error message, similar to those used in printf or vprintf.
 *            This should not be a string that comes from untrusted sources or is excessively long,
 *            as it can cause buffer overflows and other security issues.
 * @param code The error code associated with the message. It's recommended to use a well-defined range
 *             of values for this parameter to make error handling more efficient, with 0 being the most common value.
 *
 * @return If an error occurs during function execution (e.g., allocation failure), returns a non-zero value;
 *         otherwise, returns 0.
 */
int logError(const char* msg, int code, ...) {
    if ((msg == NULL) || (strlen(msg) > 1024)) { // Check for null and excessive length
        fprintf(stderr, "logError: Null or too long error message provided. Maximum allowed length is 1024 characters.\n");
        return 1;
    }

    if (code < 0) { // Validate the code range; adjust as needed based on your application's specific requirements.
        fprintf(stderr, "Invalid error code provided to logError. Code must be >= 0.\n");
        return 1;
    }

    char buffer[1024]; // Use a fixed-size buffer for safer string handling
    va_list args;

    va_start(args, msg);
    vsnprintf(buffer, sizeof(buffer), msg, args);

    if (vsnprintf(buffer, sizeof(buffer), msg, args) == -1) { // Handle case where there was an error in the vsnprintf operation.
        fprintf(stderr, "logError: Failed to log message. Possible memory allocation failure.\n");
        va_end(args);
        return 10; // Return a unique error code indicating a potential memory issue.
    }

    va_end(args);

    if (vsnprintf(buffer, sizeof(buffer), msg, args) >= sizeof(buffer)) { // Handle buffer overflow
        fprintf(stderr, "logError: Insufficient space in buffer for the entire message. Buffer size is %zu bytes.\n", sizeof(buffer));
        return 11; // Return a unique error code indicating a buffer overflow.
    } else {
        va_start(args, msg);
        vfprintf(stderr, buffer, args); // Write to standard error if the entire message fits
        va_end(args);
    }

    return 0;
}

int main() {
    logError("Something went wrong: %d", 12345);
    logError("The value of x is: %d and y is: %d.", 10, 20);
    return 0;
}
