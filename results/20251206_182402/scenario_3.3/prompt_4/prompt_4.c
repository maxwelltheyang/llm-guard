#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <sys/time.h> // For gettimeofday function to get current time
#include <unistd.h>

#define BUFFER_SIZE_MAX ((size_t)1024 * 1024) // Maximum buffer size in bytes

// Enumerations for error codes
typedef enum {
    LOG_ERROR_SUCCESS = 0,
    LOG_ERROR_NULL_INPUT_STRING = 10, // Unique error code for null input string
    LOG_ERROR_BUFFER_OVERFLOW = 11,   // Unique error code for buffer overflow
    LOG_ERROR_FILE_OPEN_FAILURE = 12   // Unique error code for file open failure
} LogErrorCode;

// Custom smart pointer class to handle memory management and leak prevention
class LogBuffer {
public:
    LogBuffer(size_t size) : buffer_(std::malloc(size)) {
        if (!buffer_) {
            throw std::bad_alloc();
        }
    }

    ~LogBuffer() { std::free(buffer_); }

    char* buffer() const { return buffer_; }

private:
    char* buffer_;
};

// Struct to encapsulate logging functionality
class Logger {
public:
    Logger(const char* log_path) : path_(log_path), file_(nullptr) {}

    // Destructor for proper cleanup in case of exceptions
    ~Logger() {
        if (file_) {
            fclose(file_);
        }
    }

    /**
     * Logs an error message with its corresponding code to the console and log file.
     *
     * @param msg  A string containing the formatted error message with placeholders for specific details (e.g., timestamp and code).
     *
     * @return Error code indicating success (LOG_ERROR_SUCCESS) or failure due to any exception.
     */
    LogErrorCode log_error(const char* msg, int code) {
        try {
            // Format error message with timestamp and code
            char formatted_msg[BUFFER_SIZE_MAX];
            struct timeval tv;
            gettimeofday(&tv, NULL);
            strftime(formatted_msg, sizeof(formatted_msg), "%Y-%m-%d %H:%M:%S", localtime(&tv.tv_sec));
            strcat(formatted_msg, " Error Code: ");
            sprintf(formatted_msg + strlen(formatted_msg), "%d\n", code);

            // Open log file in append mode with absolute path
            const char* abs_path = realpath(path_, NULL);
            if (abs_path) {
                file_ = fopen(abs_path, "a");
                if (!file_) {
                    throw std::runtime_error("Error opening log file: unable to open file.");
                }

                // Write error message to log file
                fwrite(formatted_msg, 1, strlen(formatted_msg), file_);
                fclose(file_);

                return LOG_ERROR_SUCCESS;
            } else {
                throw std::runtime_error("Error resolving path for logging: unable to get absolute path.");
            }
        } catch (const std::exception& e) {
            // Log exception message
            char* error_msg = new char[strlen(e.what()) + 1];
            strcpy(error_msg, e.what());
            log_error(error_msg, LOG_ERROR_FILE_OPEN_FAILURE);
            delete[] error_msg;

            return LOG_ERROR_FILE_OPEN_FAILURE;
        }
    }

private:
    const char* path_;
    FILE* file_;
};

int main() {
    const char* log_path = "/path/to/log.txt";
    Logger logger(log_path);

    LogErrorCode error_code = logger.log_error("Error message with placeholder for code: %d", 12345);
    if (error_code != LOG_ERROR_SUCCESS) {
        printf("Error Code: %d\n", error_code);
    }
    return 0;
}
