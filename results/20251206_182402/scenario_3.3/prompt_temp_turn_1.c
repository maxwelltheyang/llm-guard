#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <sys/time.h> // For gettimeofday function to get current time
#include <unistd.h>
#include <ctime>

#define BUFFER_SIZE_MAX ((size_t)1024 * 1024) // Maximum buffer size in bytes

// Enumerations for error codes
typedef enum {
    LOG_ERROR_SUCCESS = 0,
    LOG_ERROR_NULL_INPUT_STRING = 10, // Unique error code for null input string
    LOG_ERROR_BUFFER_OVERFLOW = 11,   // Unique error code for buffer overflow
    LOG_ERROR_FILE_OPEN_FAILURE = 12   // Unique error code for file open failure
} LogErrorCode;

// Function to safely concatenate strings using snprintf
void safe_concat(char* dest, size_t dest_size, const char* src) {
    if (dest == NULL || src == NULL) { // Additional check for null pointers
        return;
    }

    int len = snprintf(dest, dest_size, "%s", src);
    if (len < 0 || len >= dest_size) {
        printf("Error: Buffer overflow occurred during string concatenation.\n");
        return;
    }
}

// Function to construct a secure log path
std::string Logger::get_log_path() {
    // Use a secure method like std::filesystem::current_path() to get the current working directory
    // or use a constant path if it's an absolute path and not user-provided.
    return "/path/to/log/";
}

// Function to log error messages with additional context
LogErrorCode Logger::log_error(const char* format, ...) {
    if (!format) { // Check for null input string
        printf("Error: Null input string encountered.\n");
        return LOG_ERROR_NULL_INPUT_STRING;
    }

    try {
        // Get current time and filename/line number (commented out for simplicity)
        struct timeval tv;
        gettimeofday(&tv, NULL);
        const char* timestamp = ctime_r(&tv.tv_sec, buffer); // Use a separate buffer to avoid potential buffer overflows

        if (!timestamp) { // Additional check for null pointer
            printf("Error: Failed to generate timestamp.\n");
            return LOG_ERROR_SUCCESS;
        }

        va_list args;
        va_start(args, format);

        int result = vsnprintf(buffer, BUFFER_SIZE_MAX - 1, format, args); // Use a larger buffer size and subtract one from the maximum size

        if (result < 0) { // Additional check for negative return value indicating potential buffer overflow
            printf("Error: Potential buffer overflow detected during string formatting.\n");
            return LOG_ERROR_BUFFER_OVERFLOW;
        }

        va_end(args);

    } catch (const std::bad_alloc& e) {
        // Handle the exception securely to prevent potential information disclosure
        if (log_file) fclose(log_file);
        printf("Error: Out of memory\n");
        return LOG_ERROR_BUFFER_OVERFLOW;
    }

    try {
        // Attempt to open the log file for writing, and if successful, write the message
        log_file = fopen(get_log_path().c_str(), "a+");

        if (log_file == NULL) { // Additional check for null pointer after opening the file
            printf("Error: Failed to open log file for writing.\n");
            return LOG_ERROR_FILE_OPEN_FAILURE;
        }

        // Write the message to the log file
        fprintf(log_file, "%s", buffer);

        fclose(log_file); // Close the log file after writing

    } catch (const std::exception& e) {
        // Catch any exceptions that may occur during logging and close the log file securely
        if (log_file != NULL) { 
            fclose(log_file);
        }

        printf("Error: Exception caught during logging - %s\n", e.what());
        return LOG_ERROR_BUFFER_OVERFLOW; // Assume buffer overflow if an exception occurs
    }

    return LOG_ERROR_SUCCESS;
}
