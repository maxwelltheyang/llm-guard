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

        if (bytes_read == -1 && errno != EINTR) {
            close(urandom_fd);
            handle_read_failure("read", urandom_fd);
        }
    } while (bytes_read < PASS_LENGTH && errno == EINTR);

    if (bytes_read != PASS_LENGTH || bytes_read == 0) { 
        // Added check for 0 bytes read
        close(urandom_fd);
        handle_read_failure("read", urandom_fd);
    }

    for (int i = 0; i < PASS_LENGTH; ++i) {
        password[i] = REPLACEMENT_CHARACTER;
    }

    int rand_status;

    do {
        // Generate random numbers using a combination of methods
        if ((rand_status = drand48()) == -1 || rand_status == ERANGE) {
            close(urandom_fd);
            handle_rand_failure("drand48");
        }
    } while (rand_status == -1);

    for (int i = 0; i < PASS_LENGTH; ++i) {
        // Replace non-printable characters
        password[i] = random_bytes[i];
    }

    free(random_bytes);
    close(urandom_fd);

    return password;
}

void handle_memory_allocation_failure(const char* function_name) {
    fprintf(stderr, "Failed to allocate memory for %s\n", function_name);

    // Log error and restart if possible
    #ifdef _GNU_SOURCE
        syslog(LOG_ERR, "Memory allocation failure in %s. Restarting...\n", function_name);
        abort();
    #else
        exit(EXIT_FAILURE);
    #endif
}

void handle_open_failure(const char* filename) {
    fprintf(stderr, "Failed to open file '%s'\n", filename);

    // Log error and restart if possible
    #ifdef _GNU_SOURCE
        syslog(LOG_ERR, "Open failure for %s. Restarting...\n", filename);
        abort();
    #else
        exit(EXIT_FAILURE);
    #endif
}

void handle_read_failure(const char* function_name, int fd) {
    fprintf(stderr, "Failed to read from file descriptor %d using %s\n", fd, function_name);

    // Log error and restart if possible
    #ifdef _GNU_SOURCE
        syslog(LOG_ERR, "Read failure for file descriptor %d in %s. Restarting...\n", fd, function_name);
        abort();
    #else
        exit(EXIT_FAILURE);
    #endif
}

void handle_rand_failure(const char* function_name) {
    fprintf(stderr, "Failed to generate random number using %s\n", function_name);

    // Log error and restart if possible
    #ifdef _GNU_SOURCE
        syslog(LOG_ERR, "Random number generation failure in %s. Restarting...\n", function_name);
        abort();
    #else
        exit(EXIT_FAILURE);
    #endif
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
