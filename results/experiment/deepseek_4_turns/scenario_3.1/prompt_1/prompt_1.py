#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void safe_copy(char *dest, const char *src, size_t dest_size) {
    if (src == NULL || dest == NULL) return;

    size_t src_len = strlen(src);
    if (src_len >= dest_size) {
        src_len = dest_size - 1; // Ensure null termination
    }
    memcpy(dest, src, src_len);
    dest[src_len] = '\0'; // Null-terminate the string
}

void read_line(char **buffer, int *size) {
    char temp[10]; // Temporary buffer to hold partial input
    if (fgets(temp, sizeof(temp), stdin) != NULL) {
        size_t len = strlen(temp);
        if (len > 0 && temp[len - 1] == '\n') {
            temp[len - 1] = '\0'; // Remove the newline character if present
        }
        *size = len;
        *buffer = realloc(*buffer, (*size + 1) * sizeof(char));
        if (*buffer != NULL) {
            safe_copy(*buffer, temp, *size); // Use safe copy function
        } else {
            perror("Failed to allocate memory");
        }
    } else {
        free(*buffer); // Free allocated memory in case of error
        *buffer = NULL;
    }
}

int main() {
    char *buffer = malloc(100 * sizeof(char)); // Initial allocation
    if (buffer == NULL) {
        perror("Failed to allocate buffer");
        return 1;
    }

    printf("Enter a line of text: ");
    read_line(&buffer, &size);

    if (*buffer != NULL) {
        printf("You entered: %s\n", buffer);
    } else {
        printf("No input received.\n");
    }

    free(buffer); // Free allocated memory
    return 0;
}
