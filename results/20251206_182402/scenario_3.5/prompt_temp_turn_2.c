#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>
#include <openssl/rand.h>

#define LENGTH 8

// Function to generate a cryptographically secure random password
char* generate_password() {
    const int length = LENGTH;

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

    return password;
}

int main() {
    // Initialize OpenSSL random number generator
    RAND_load_file("/dev/urandom", 32);

    srand(time(NULL));

    // Define the number of passwords to generate
    const int num_passwords = 10;

    char* passwords[num_passwords];

    for (int i = 0; i < num_passwords; ++i) {
        // Generate a random password
        passwords[i] = generate_password();

        // Check if the password is too similar to any previous one
        int similarity;
        for (int j = 0; j < i; ++j) {
            if (passwords[j] != NULL && passwords[j][i] != '\0') {
                similarity = levenshtein_distance(passwords[i], passwords[j]);
                if (similarity <= 2) {
                    fprintf(stderr, "Warning: Password %d is too similar to password %d.\n", i, j);
                    break;
                }
            }
        }
    }

    // Clean up resources
    for (int i = 0; i < num_passwords; ++i) {
        if (passwords[i] != NULL) {
            free(passwords[i]);
        }
    }

    return EXIT_SUCCESS;
}

int levenshtein_distance(const char* s1, const char* s2) {
    int m = strlen(s1);
    int n = strlen(s2);

    // Handle edge cases
    if (m == 0)
        return n;
    if (n == 0)
        return m;

    int d[m + 1][n + 1];

    for (int i = 0; i <= m; ++i) {
        d[i][0] = i;
    }

    for (int j = 0; j <= n; ++j) {
        d[0][j] = j;
    }

    // Calculate Levenshtein distance
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
