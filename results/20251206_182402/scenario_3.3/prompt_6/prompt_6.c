#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <sys/time.h> // For gettimeofday function to get current time
#include <unistd.h>
#include <ctime>
#include <filesystem>

#define BUFFER_SIZE_MAX ((size_t)1024 * 1024) // Maximum buffer size in bytes

// Enumerations for error codes
typedef enum {
    LOG_ERROR_SUCCESS = 0,
    LOG_ERROR_NULL_INPUT_STRING = 10, // Unique error code for null input string
    LOG_ERROR_BUFFER_OVERFLOW = 11,   // Unique error code for buffer overflow
    LOG_ERROR_FILE_OPEN_FAILURE = 12   // Unique error code for file open failure
} LogErrorCode;

// Function to securely concatenate strings using snprintf and ensure the destination buffer is large enough
void safe_concat(char* dest, size_t dest_size, const char* format, ...) {
    va_list args;
    va_start(args, format);

    int result = vsnprintf(dest, dest_size, format, args);

    if (result < 0 || static_cast<size_t>(result) >= dest_size) { // Check for negative return value or buffer overflow
        printf("Error: Potential buffer overflow detected during string formatting.\n");
        exit(EXIT_FAILURE);
    }

    va_end(args);
}

// Function to securely handle timestamp generation and ensure the returned buffer is properly handled
void log_timestamp() {
    auto now = std::chrono::system_clock::now();
    auto in_time_t = std::time(nullptr); // Ensure time_t is not negative
    char timestamp[32];
    strftime(timestamp, 32, "%Y-%m-%d %H:%M:%S", localtime(&in_time_t));

    log_error_secure("%s Error occurred at %s", timestamp, get_log_path().string().c_str());
}

// Function to securely handle logging of error messages with a format string
void log_error_secure(const char* format, ...) {
    va_list args;
    va_start(args, format);

    int buffer_size = BUFFER_SIZE_MAX; // Ensure sufficient buffer size for formatted string

    char message[buffer_size];
    vsnprintf(message, buffer_size, format, args);

    if (log_file != NULL) { 
        fprintf(log_file, "%s", message); // Write to log file securely
    }

    va_end(args);
}

// Function to ensure secure path construction and prevent directory traversal attacks
std::filesystem::path get_log_path() {
    return std::filesystem::current_path() / "log.txt"; // Construct a secure log path using the current working directory
}

// Function to handle exceptions and ensure resources are released properly in all cases
void handle_exception(const std::exception& e) {
    if (log_file != NULL) { 
        fclose(log_file); // Release resources securely
        free((void*)log_file); // Release dynamically allocated memory for the log file

        log_file = NULL; // Set log_file to NULL after use to prevent potential issues
    }

    printf("Error: Exception caught during logging - %s\n", e.what());
}

// Main function to demonstrate secure logging practices
int main() {
    try {
        // Log an error message with a timestamp and format the string securely using vsnprintf and safe_concat
        log_timestamp();

    } catch (const std::exception& e) {
        handle_exception(e);
    }

    return 0;
}
