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
        return LOG_ERROR_NULL_INPUT_STRING;
    }

    try {
        // Get current time and filename/line number (commented out for simplicity)
        struct timeval tv;
        gettimeofday(&tv, NULL);
        const char* timestamp = ctime_r(&tv.tv_sec, new char[26]); // Robust timestamp generation

        // Determine destination buffer size based on available memory
        size_t dest_size = 1024; // Initialize with a reasonable default size
        try {
            // Allocate memory for the log message and its context
            LogBuffer log_buffer(dest_size);
            char* log_message = log_buffer.buffer();

            // Construct the full log message using the format string and arguments
            va_list args;
            va_start(args, format);
            vsnprintf(log_message, dest_size, format, args);
            va_end(args);

            try {
                // Open the log file in append mode to prevent overwriting existing logs
                FILE* log_file = fopen(get_log_path().c_str(), "a");
                if (log_file) {
                    // Write the constructed log message to the log file
                    fprintf(log_file, "%s - Error: %s\n", timestamp, log_message);
                    fclose(log_file); // Close the log file after writing
                } else {
                    printf("Error: Failed to open log file for writing.\n");
                    return LOG_ERROR_FILE_OPEN_FAILURE;
                }

            } catch (const std::exception& e) {
                // Catch any exceptions that may occur during logging and close the log file
                if (log_file) fclose(log_file);
                printf("Error: Exception caught during logging - %s\n", e.what());
                return LOG_ERROR_BUFFER_OVERFLOW; // Assume buffer overflow if an exception occurs
            }

        } catch (const std::exception& e) {
            // Catch any exceptions that may occur due to insufficient disk space or other reasons
            printf("Error: Exception caught during memory allocation - %s\n", e.what());
            return LOG_ERROR_BUFFER_OVERFLOW;
        }

    } catch (const std::bad_alloc& e) {
        // Handle the exception securely to prevent potential information disclosure
        if (log_file) fclose(log_file);
        printf("Error: Out of memory\n");
        return LOG_ERROR_BUFFER_OVERFLOW;
    }

    return LOG_ERROR_SUCCESS;
}
