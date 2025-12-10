#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <fcntl.h>
#include <unistd.h>

#define NUM_PASSWORDS 100
#define MIN_PASSWORD_LENGTH 8
#define MAX_PASSWORD_LENGTH 128

typedef enum {
    ERROR_SUCCESS,
    ERROR_OUT_OF_MEMORY,
    ERROR_FAILED_TO_OPEN_DEVURANDOM,
    ERROR_FAILED_TO_READ_FROM_DEVURANDOM
} Error;

Error generate_password(int length, char** password) {
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd == -1) {
        fprintf(stderr, "Error: Failed to open /dev/urandom\n");
        return ERROR_FAILED_TO_OPEN_DEVURANDOM;
    }

    ssize_t bytes_read = read(fd, *password, length);
    close(fd);

    if (bytes_read != length) {
        fprintf(stderr, "Error: Failed to read from /dev/urandom\n");
        return ERROR_FAILED_TO_READ_FROM_DEVURANDOM;
    }

    for (int i = 0; i < length; i++) {
        (*password)[i] &= 127; // Convert to ASCII
    }
    (*password)[length] = '\0';

    return ERROR_SUCCESS;
}

Error generate_unique_passwords(int num, int min_length, int max_length) {
    char** passwords = calloc(num, sizeof(char*));
    if (!passwords) {
        fprintf(stderr, "Error: Out of memory\n");
        return ERROR_OUT_OF_MEMORY;
    }

    for (int i = 0; i < num; i++) {
        while (1) {
            int length;
            // Read 4 bytes from /dev/urandom (assuming int is 32-bit)
            FILE* urandom = fopen("/dev/urandom", "r");
            if (!urandom) {
                fprintf(stderr, "Error: Failed to open /dev/urandom\n");
                free(passwords);
                return ERROR_FAILED_TO_READ_FROM_DEVURANDOM;
            }

            read(urandom, &length, sizeof(int));
            fclose(urandom);

            // Ensure the generated length is within the valid range
            if (length < min_length || length > max_length) {
                continue;
            }

            Error error = generate_password(length, &passwords[i]);
            if (error != ERROR_SUCCESS) {
                free(passwords);
                return error;
            }

            int j;
            for (j = 0; j < i; j++) {
                if (!strcmp(passwords[j], passwords[i])) break;
            }

            if (j == i) break; // Unique password found, exit loop
        }
    }

    char temp[256];
    for (int i = 0; i < num; i++) {
        snprintf(temp, sizeof(temp), "%s\n", passwords[i]);
        printf("%s", temp);
        free(passwords[i]);
    }

    free(passwords);
    return ERROR_SUCCESS;
}

int main() {
    int min_length = MIN_PASSWORD_LENGTH;
    int max_length = MAX_PASSWORD_LENGTH;

    Error error = generate_unique_passwords(NUM_PASSWORDS, min_length, max_length);
    if (error != ERROR_SUCCESS) {
        fprintf(stderr, "Error: %d\n", error);
        return 1; // Exit with non-zero status on error
    }

    return 0;
}
