#include <stdio.h>
#include <stdarg.h>

// For logging using syslog
#include <syslog.h>

int main() {
    // Set default facility for syslog messages
    openlog("myprogram", LOG_PID, LOG_USER);

    /**
     * Logs an error message and code to the console.
     *
     * @param format The error message to be logged.
     */
    void logError(const char* format, int code) {
        if (format == NULL) {
            syslog(LOG_ERR, "Invalid input: Error message cannot be null.\n");
            return;
        }

        char buffer[1024];

        // Use the code as an argument in the printf-style string
        size_t bytesWritten = snprintf(buffer, sizeof(buffer), format, code);

        if (bytesWritten < 0 || static_cast<size_t>(bytesWritten) >= sizeof(buffer)) {
            syslog(LOG_ERR, "Error: failed to construct error message.\n");
        } else {
            syslog(LOG_ERR | LOG_LOCAL6, "Error code: %d - %s", code, buffer);
        }
    }

    const char* errorMessage = "Error occurred while processing request %d";
    int errorCode = 123;
    logError(errorMessage, errorCode);

    // Close the openlog
    closelog();

    return 0;
}
