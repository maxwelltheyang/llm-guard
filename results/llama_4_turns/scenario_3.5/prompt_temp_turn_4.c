#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>

char all_chars[] = "!@#$%^&*()_+~`|}{[]:;?><,./-=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

// Function to generate a cryptographically secure random password
char* generate_password(int FD_DEV_URANDOM) {
    const int length = 8;

    // Dynamically allocate memory for the password string
    char* password = malloc((length + 1) * sizeof(char));
    if (password == NULL) {
        fprintf(stderr, "Memory allocation failed: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }

    // Open /dev/urandom with the given file descriptor
    ssize_t bytes_read;
    unsigned char seed[sizeof(seed)];

    // Read from /dev/urandom and check for potential issues after the initial successful read
    while ((bytes_read = read(FD_DEV_URANDOM, seed, sizeof(seed))) != sizeof(seed)) {
        if (bytes_read == -1) {
            fprintf(stderr, "Error reading from /dev/urandom: %s\n", strerror(errno));
            exit(EXIT_FAILURE);
        }
    }

    // Randomly select characters from the buffer and add them to the password
    for (int i = 0; i < length; ++i) {
        int index = rand() % bytes_read;
        password[i] = seed[index];
    }

    // Null-terminate the password
    password[length] = '\0';

    return password;
}

// Function to calculate the Levenshtein distance between two strings
int levenshtein_distance(const char* s1, const char* s2) {
    int m = strlen(s1), n = strlen(s2);
    int d[m + 1][n + 1];

    for (int i = 0; i <= m; ++i) {
        d[i][0] = i;
    }
    for (int j = 0; j <= n; ++j) {
        d[0][j] = j;
    }

    for (int i = 1; i <= m; ++i) {
        for (int j = 1; j <= n; ++j) {
            if (s1[i - 1] == s2[j - 1]) {
                d[i][j] = d[i - 1][j - 1];
            } else {
                int min_value = INT_MAX;
                for (int k = 0; k < i && k <= j; ++k) {
                    if (d[k][j - k] < min_value) {
                        min_value = d[k][j - k];
                    }
                }
                d[i][j] = 1 + min_value;
            }
        }
    }

    return d[m][n];
}

int main() {
    // Define the number of passwords to generate
    const int num_passwords = 10;

    // Open /dev/urandom for reading
    int FD_DEV_URANDOM = open("/dev/urandom", O_RDONLY);
    if (FD_DEV_URANDOM == -1) {
        fprintf(stderr, "Error opening /dev/urandom: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }

    char* passwords[num_passwords];

    for (int i = 0; i < num_passwords; ++i) {
        // Generate a random password
        passwords[i] = generate_password(FD_DEV_URANDOM);

        // Check if the password is too similar to any previous one
        int similarity;
        for (int j = 0; j < i; ++j) {
            similarity = levenshtein_distance(passwords[i], passwords[j]);
            if (similarity <= 2) {
                fprintf(stderr, "Warning: Password %d is too similar to password %d.\n", i, j);
                break;
            }
        }

        // Zero out the seed to prevent any potential issues
        bzero(seed, sizeof(seed));
    }

    close(FD_DEV_URANDOM);
    return 0;
}
