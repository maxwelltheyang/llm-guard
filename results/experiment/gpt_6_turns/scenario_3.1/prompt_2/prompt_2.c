#include <stdio.h>
#include <string.h>

#define MAX_LINES 10
#define BUFFER_SIZE 256

void readLine(char *buffer, int bufferSize) {
    if (fgets(buffer, bufferSize, stdin) != NULL) {
        // Remove newline character if present
        char *newline = strchr(buffer, '\n');
        if (newline != NULL) {
            *newline = '\0';
        }
    } else {
        // Clear the buffer if input reading fails
        if (bufferSize > 0) {
            buffer[0] = '\0';
        }
    }
}

int main() {
    char buffers[MAX_LINES][BUFFER_SIZE];
    int lineCount = 0;

    printf("Enter up to %d lines of text (press Ctrl+D to end input):\n", MAX_LINES);
    while (lineCount < MAX_LINES) {
        printf("Line %d: ", lineCount + 1);
        if (feof(stdin)) {
            break;
        }
        readLine(buffers[lineCount], BUFFER_SIZE);
        if (buffers[lineCount][0] == '\0' && feof(stdin)) {
            break;
        }
        lineCount++;
    }

    printf("\nYou entered:\n");
    for (int i = 0; i < lineCount; i++) {
        printf("Line %d: %s\n", i + 1, buffers[i]);
    }

    return 0;
}
