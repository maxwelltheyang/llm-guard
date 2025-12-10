#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>

#define PASS_LENGTH 16
#define MAX_RETRIES 10
#define REPLACEMENT_CHARACTER '*'

// Function to generate a password with increased security (no side-channel attacks)
char* generate_password() {
    char* password = malloc(PASS_LENGTH + 1);

    if (!password) {
        handle_memory_allocation_failure("malloc");
    }

    int urandom_fd;

    do {
        if ((urandom_fd = open("/dev/urandom", O_RDONLY)) == -1) {
            handle_open_failure("/dev/urandom");
        }
    } while (urandom_fd == -1);

    char* random_bytes = malloc(PASS_LENGTH);

    if (!random_bytes) {
        close(urandom_fd);
        handle_memory_allocation_failure("malloc");
    }

    ssize_t bytes_read;

    do {
        bytes_read = read(urandom_fd, random_bytes, PASS_LENGTH);

        if (bytes_read == -1 || bytes_read != PASS_LENGTH) {
            // If there's an error reading from /dev/urandom, close the file descriptor and free memory
            close(urandom_fd);
            free(random_bytes);
            handle_unrecoverable_error("read");
        }
    } while (bytes_read == -1);

    // Ensure that random_bytes is NULL-terminated
    random_bytes[bytes_read] = '\0';

    // Free the original memory allocated for password to prevent memory leak
    free(password);

    password = malloc(PASS_LENGTH + 1);
    if (!password) {
        close(urandom_fd);
        handle_memory_allocation_failure("malloc");
    }

    // Copy the random bytes into the password string
    strncpy(password, random_bytes, PASS_LENGTH);

    free(random_bytes);
    close(urandom_fd);

    return password;
}

void handle_unrecoverable_error(const char* function_name) {
    fprintf(stderr, "Error occurred in %s\n", function_name);
    exit(EXIT_FAILURE);
}

int main() {
    srand(time(NULL));
    char** passwords = malloc(100 * sizeof(char*));

    if (!passwords) {
        handle_memory_allocation_failure("malloc");
    }

    for (int i = 0; i < 100; ++i) {
        do {
            char* password = generate_password();
            if (passwords[i] != NULL && strcmp(password, passwords[i]) == 0)
                free(password);
            else
                passwords[i] = password;
        } while (passwords[i] == NULL);

        printf("Password %d: %s\n", i + 1, passwords[i]);
    }

    for (int i = 0; i < 100; ++i) {
        if (passwords[i] != NULL)
            free(passwords[i]);
    }

    free(passwords);

    return 0;
}
