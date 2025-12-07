#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <sys/time.h> // For gettimeofday function to get current time
#include <unistd.h>

#define BUFFER_SIZE_MAX ((size_t)1024 * 1024) // Maximum buffer size in bytes

/**
 * Logs an error message with its corresponding code to the console and log file.
 *
 * @param msg The format string for the error message, similar to those used in printf or vprintf.
 *            This should not be a string that comes from untrusted sources or is excessively long,
 *            as it can cause buffer overflows and other security issues.
 * @param code The error code associated with the message. It's recommended to use a well-defined range
 *             of values for this parameter to make error handling more efficient, with 0 being the most common value.
 *
 * @return A non-zero value if an error occurs during function execution (e.g., allocation failure, file operation issues);
 *         otherwise, returns 0.
 */
int logError(const char* msg, int code, ...) {
    if ((msg == NULL) || (strnlen(msg, BUFFER_SIZE_MAX) > BUFFER_SIZE_MAX - 1)) { // Check for null and excessive length
        fprintf(stderr, "logError: Null or excessively long input string.\n");
        return 1;
    }

    va_list args;
    va_start(args, code);

    size_t n = 0; // Initialize buffer size to avoid integer overflow issues

    do {
        char* buffer = malloc(BUFFER_SIZE_MAX); // Allocate a dynamic buffer with max size
        if (buffer == NULL) { // Handle case where there was an error in the malloc operation
            fprintf(stderr, "logError: Failed to log message. Possible memory allocation failure.\n");
            va_end(args);
            return 10; // Return a unique error code indicating a potential memory issue.
        }

        vsnprintf(buffer, BUFFER_SIZE_MAX, msg, args); // Store formatted string in buffer

        if ((strnlen(buffer, BUFFER_SIZE_MAX) > BUFFER_SIZE_MAX - 1)) { // Check if entire message fits
            fprintf(stderr, "logError: Buffer size is %zu bytes but the entire error message exceeds this limit.\n", BUFFER_SIZE_MAX);
            free(buffer); // Free allocated buffer and return unique error code indicating a buffer overflow.
            va_end(args);
            return 11;
        } else {
            vfprintf(stderr, buffer, args); // Write to standard error if the entire message fits
            free(buffer);
        }

        struct timeval tv;
        gettimeofday(&tv, NULL); // Get current time for timestamp
        char timestamp[32];
        sprintf(timestamp, "[%Y-%m-%dT%H:%M:%S.%03ld]", (long)tv.tv_sec, (long int)((double)tv.tv_usec / 1000));

        FILE* log_file = fopen("log.txt", "a"); // Append to a log file in append mode
        if (!log_file) {
            fprintf(stderr, "logError: Failed to open log file for writing.\n");
            va_end(args);
            return 12; // Return unique error code indicating failure to open log file.
        }
        fprintf(log_file, "%s %d\n", timestamp, code);
        fclose(log_file);

        va_end(args);
    } while (0);

    return 0;
}

int main() {
    char* msg = "Error message with a very long format string that might cause buffer overflows if not handled properly.";
    int error_code = logError(msg, 12345); // Return error code instead of printing it
    printf("Error Code: %d\n", error_code);
    return 0;
}
