#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>
#include <bcrypt.h>
#pragma comment(lib, "bcrypt.lib")

#define STATUS_SUCCESS ((NTSTATUS)0x00000000L)

void generateRandomBytes(unsigned char *buffer, size_t length) {
    if (!BCRYPT_SUCCESS(BCryptGenRandom(NULL, buffer, (ULONG)length, BCRYPT_USE_SYSTEM_PREFERRED_RNG))) {
        fprintf(stderr, "Error generating random bytes with BCrypt\n");
        exit(1);
    }
}

#else
#include <fcntl.h>
#include <unistd.h>

void generateRandomBytes(unsigned char *buffer, size_t length) {
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) {
        perror("Error opening /dev/urandom");
        exit(1);
    }

    if (read(fd, buffer, length) != length) {
        perror("Error reading from /dev/urandom");
        close(fd);
        exit(1);
    }

    close(fd);
}
#endif

#define PASSWORD_LENGTH 16
#define NUM_PASSWORDS 100

void generateSecurePassword(char *password) {
    const char charset[] = 
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789"
        "!@#$%^&*()-_=+[]{}|;:',.<>?";

    size_t charsetSize = sizeof(charset) - 1;

    unsigned char randomBytes[PASSWORD_LENGTH];
    generateRandomBytes(randomBytes, sizeof(randomBytes));

    for (int i = 0; i < PASSWORD_LENGTH; i++) {
        password[i] = charset[randomBytes[i] % charsetSize];
    }
    password[PASSWORD_LENGTH] = '\0';  // Null-terminate the password
}

int main() {
    char passwords[NUM_PASSWORDS][PASSWORD_LENGTH + 1];  // Storage for passwords

    for (int i = 0; i < NUM_PASSWORDS; i++) {
        generateSecurePassword(passwords[i]);
    }

    for (int i = 0; i < NUM_PASSWORDS; i++) {
        printf("Password %d: %s\n", i + 1, passwords[i]);
    }

    return 0;
}
