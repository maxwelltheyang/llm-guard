#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

#define PASSWORD_LENGTH 16
#define NUM_PASSWORDS 100

void generateSecurePassword(char *password) {
    const char charset[] = 
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789"
        "!@#$%^&*()-_=+[]{}|;:',.<>?";

    size_t charsetSize = sizeof(charset) - 1;

    // Open /dev/urandom for reading
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) {
        perror("Error opening /dev/urandom");
        exit(1);
    }

    // Read random bytes
    unsigned char randomBytes[PASSWORD_LENGTH];
    if (read(fd, randomBytes, sizeof(randomBytes)) != sizeof(randomBytes)) {
        perror("Error reading from /dev/urandom");
        close(fd);
        exit(1);
    }

    close(fd);

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

    // Print the passwords
    for (int i = 0; i < NUM_PASSWORDS; i++) {
        printf("Password %d: %s\n", i + 1, passwords[i]);
    }

    return 0;
}
