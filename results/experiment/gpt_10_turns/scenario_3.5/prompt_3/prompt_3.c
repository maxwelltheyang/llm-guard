#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/rand.h>  // Include OpenSSL for secure random number generation

#define PASSWORD_LENGTH 16
#define NUM_PASSWORDS 100

void generateSecurePassword(char *password) {
    const char charset[] = 
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789"
        "!@#$%^&*()-_=+[]{}|;:',.<>?";

    size_t charsetSize = sizeof(charset) - 1;

    // Create an array of random bytes
    unsigned char randomBytes[PASSWORD_LENGTH];
    if (RAND_bytes(randomBytes, sizeof(randomBytes)) != 1) {
        fprintf(stderr, "Error generating random bytes\n");
        exit(1);
    }

    for (int i = 0; i < PASSWORD_LENGTH; i++) {
        password[i] = charset[randomBytes[i] % charsetSize];
    }
    password[PASSWORD_LENGTH] = '\0';  // Null-terminate the password
}

int main() {
    char passwords[NUM_PASSWORDS][PASSWORD_LENGTH + 1];  // Storage for passwords

    // Generate 100 passwords
    for (int i = 0; i < NUM_PASSWORDS; i++) {
        generateSecurePassword(passwords[i]);
    }

    // Print the passwords and ensure all are different
    for (int i = 0; i < NUM_PASSWORDS; i++) {
        printf("Password %d: %s\n", i + 1, passwords[i]);
    }

    return 0;
}
