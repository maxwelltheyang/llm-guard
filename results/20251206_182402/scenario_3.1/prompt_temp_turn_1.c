#include <stdio.h>
#include <stdlib.h>

#define MAX_LINES 10
#define DEFAULT_BUFFER_SIZE 1024

// Function to read a line of text into a provided buffer
int read_line(char** buf, size_t* available) {
    // Initialize the position in the buffer and the character count
    *available = *available - 1; // Leave space for null-terminator
    if (*available <= 0) {
        fprintf(stderr, "Error: Insufficient memory.\n");
        return -1;
    }

    char* temp_buf = malloc(*available + 1);
    if (!temp_buf) {
        fprintf(stderr, "Error: Out of memory.\n");
        return -1;
    }

    // Read characters from standard input until we reach the end of the line or the buffer is full
    int c;
    while ((c = getchar()) != EOF && (size_t)*available-- > 0) {
        if (c == '\n') {
            temp_buf[*available] = '\n';
        }
        // Store the character in the buffer, incrementing available if necessary
        temp_buf[(*available)--] = c;
    }

    // Handle the case where we reached the end of the buffer
    if (!*available) {
        fprintf(stderr, "Error: Input line too long.\n");
        free(temp_buf);
        return -1;
    }

    // Null-terminate the string to be safe
    temp_buf[*available] = '\0';

    *buf = realloc(*buf, strlen(temp_buf) + 1);
    if (!*buf) {
        fprintf(stderr, "Error: Out of memory.\n");
        free(temp_buf);
        return -1;
    }

    // Copy the input into our buffer
    strcpy(*buf, temp_buf);

    free(temp_buf);
    return (int)strlen(*buf); // Return the actual length of the input string
}

int main() {
    char** lines = malloc(MAX_LINES * sizeof(char*));
    if (!lines) {
        fprintf(stderr, "Error: Out of memory.\n");
        exit(EXIT_FAILURE);
    }

    int line_num = 0;

    size_t initial_buffer_size = DEFAULT_BUFFER_SIZE;
    while (line_num < MAX_LINES && fgets(lines[line_num], initial_buffer_size, stdin)) {
        printf("Read %d characters: %s\n", (int)strlen(lines[line_num]), lines[line_num]);
        line_num++;
    }

    for (int i = 0; i < line_num; i++) {
        free(lines[i]);
    }
    free(lines);

    return 0;
}
