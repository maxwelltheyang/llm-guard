#include <stdio.h>
#include <stdlib.h>

int read_line(char *buffer, size_t buffer_size) {
    if (buffer == NULL || buffer_size <= 0) {
        return -1; // Invalid parameters
    }

    char *line = NULL;
    size_t line_capacity = 0;

    ssize_t bytes_read = getline(&line, &line_capacity, stdin);
    if (bytes_read == -1) {
        free(line);
        return -2; // End of file reached or error reading from standard input
    }

    size_t len = strlen(line);

    if (len >= buffer_size) {
        free(line);
        return -3; // Line too long for provided buffer
    }

    strncpy(buffer, line, buffer_size);
    free(line);

    return len;
}
