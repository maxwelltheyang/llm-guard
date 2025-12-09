#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <openssl/rand.h>  // Include OpenSSL for secure random number generation

#define PASSWORD_LENGTH 16

void generateSecurePassword(char *password) {
    const char charset[] = 
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789"
        "!@#$%^&*()-_=+[]{}|;:',.<>?";

    size_t charsetSize = sizeof(charset) - 1;

    // Generate secure random bytes
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
    char password[PASSWORD_LENGTH + 1];  // +1 for null terminator
    generateSecurePassword(password);
    printf("Generated Secure Password: %s\n", password);
    return 0;
}
