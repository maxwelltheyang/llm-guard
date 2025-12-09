#include <stdio.h>
#include <stdlib.h>

#if defined(_WIN32) || defined(_WIN64)
#include <Windows.h>
#include <bcrypt.h>
#define SECURE_RANDOM(dst, size) (BCryptGenRandom(NULL, (UCHAR*)(dst), (ULONG)(size), BCRYPT_USE_SYSTEM_PREFERRED_RNG) == 0)
#else
#include <fcntl.h>
#include <unistd.h>
#define SECURE_RANDOM(dst, size) (getrandom((dst), (size), 0) != -1)
#endif

int generate_secure_random_number(int min, int max) {
    unsigned int num;
    if (!SECURE_RANDOM(&num, sizeof(num))) {
        fprintf(stderr, "Failed to generate a secure random number\n");
        exit(1);
    }
    return (num % (max - min + 1)) + min;
}

void generate_password(char *password, size_t length) {
    const char charset[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                           "abcdefghijklmnopqrstuvwxyz"
                           "0123456789"
                           "!@#$%^&*()-_=+[]{}|;:,.<>?";
    size_t charset_length = sizeof(charset) - 1;

    for (size_t i = 0; i < length; i++) {
        int index = generate_secure_random_number(0, charset_length - 1);
        password[i] = charset[index];
    }
    password[length] = '\0'; // Null-terminate the password
}

int main() {
    size_t password_length = 8;
    char password[password_length + 1];

    generate_password(password, password_length);

    printf("Generated Password: %s\n", password);

    return 0;
}
