#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#ifdef _WIN32
#include <windows.h>
#include <bcrypt.h>

// Function to generate a cryptographically secure random number on Windows
int secureRand()
{
    uint32_t randomNumber = 0;
    if (BCryptGenRandom(NULL, (PUCHAR)&randomNumber, sizeof(randomNumber), BCRYPT_USE_SYSTEM_PREFERRED_RNG) != 0) {
        fprintf(stderr, "Error generating random number.\n");
        exit(EXIT_FAILURE);
    }
    return randomNumber;
}

#else
#include <fcntl.h>
#include <unistd.h>

// Function to generate a cryptographically secure random number on Unix-like systems
int secureRand()
{
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd == -1) {
        fprintf(stderr, "Error opening /dev/urandom.\n");
        exit(EXIT_FAILURE);
    }
    uint32_t randomNumber = 0;
    if (read(fd, &randomNumber, sizeof(randomNumber)) != sizeof(randomNumber)) {
        fprintf(stderr, "Error reading random number.\n");
        exit(EXIT_FAILURE);
    }
    close(fd);
    return randomNumber;
}
#endif

void generatePassword(char *password, int length) {
    const char charset[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()";
    int charsetSize = strlen(charset);
    for (int i = 0; i < length; i++) {
        int randomIndex = secureRand() % charsetSize;
        password[i] = charset[randomIndex];
    }
    password[length] = '\0'; // Null-terminate the string
}

int main() {
    int passwordLength = 16; // Allow a longer password for more security
    char password[passwordLength + 1];

    generatePassword(password, passwordLength);
    printf("Generated Password: %s\n", password);
    return 0;
}
