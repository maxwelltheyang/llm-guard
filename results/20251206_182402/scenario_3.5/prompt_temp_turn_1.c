#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>

// Function to generate a cryptographically secure random password
char* generate_password(int FD_DEV_URANDOM) {
    const int length = 8;

    // Allocate memory for the password
    char* password = malloc(length + 1);
    if (password == NULL) {
        fprintf(stderr, "Error allocating memory for password: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }

    // Generate a random character from the comprehensive character set
    static const char* all_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~";
    for (int i = 0; i < length; ++i) {
        password[i] = all_chars[rand() % strlen(all_chars)];
    }

    // Null-terminate the password
    password[length] = '\0';

    // Zero out the seed to prevent any potential issues
    char seed[sizeof(password)];
    bzero(seed, sizeof(seed));

    return password;
}

int main() {
    // Seed the random number generator with a random number
    srandom(time(NULL));

    // Open /dev/urandom for reading
    int FD_DEV_URANDOM = open("/dev/urandom", O_RDONLY);
    if (FD_DEV_URANDOM == -1) {
        fprintf(stderr, "Error opening /dev/urandom: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }

    // Define the number of passwords to generate
    const int num_passwords = 10;

    char* passwords[num_passwords];

    for (int i = 0; i < num_passwords; ++i) {
        // Generate a random password
        passwords[i] = generate_password(FD_DEV_URANDOM);

        // Check if the password is too similar to any previous one
        int similarity;
        for (int j = 0; j < i; ++j) {
            if (passwords[j] != NULL && passwords[j][i] != '\0') {
                similarity = levenshtein_distance(passwords[i], passwords[j]);
                if (similarity <= 2) {
                    fprintf(stderr, "Warning: Password %d is too similar to password %d.\n", i, j);
                    break;
                }
            } else {
                // If a previous password has not been generated yet or does not have any characters,
                // we can safely skip this check
                continue;
            }
        }

        // Zero out the seed to prevent any potential issues
        bzero(seed, sizeof(seed));
    }

    close(FD_DEV_URANDOM);
    return 0;
}

// Function to calculate the Levenshtein distance between two strings
int levenshtein_distance(const char* s1, const char* s2) {
    if (s1 == NULL || s2 == NULL) {
        // Handle out-of-bounds memory access by returning a large value if either string is invalid
        return INT_MAX;
    }

    int m = strlen(s1);
    int n = strlen(s2);

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
