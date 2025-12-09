#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32) || defined(_WIN64)
#include <Windows.h>
#include <bcrypt.h>
#define SECURE_RANDOM(dst, size) (BCryptGenRandom(NULL, (UCHAR*)(dst), (ULONG)(size), BCRYPT_USE_SYSTEM_PREFERRED_RNG) == 0)
#include <wincrypt.h>
#else
#include <fcntl.h>
#include <unistd.h>
#include <openssl/sha.h> // Ensure OpenSSL is available
#define SECURE_RANDOM(dst, size) (getrandom((dst), (size), 0) != -1)
#endif

#define HASH_SIZE 65 // Size for SHA-256 in hex form (32 * 2 + 1)

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

void calculate_sha256(const char *data, char *hash_output) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, data, strlen(data));
    SHA256_Final(hash, &sha256);
    for(int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(hash_output + (i * 2), "%02x", hash[i]);
    }
    hash_output[HASH_SIZE - 1] = '\0'; // Ensure null-termination here
}

int main() {
    size_t password_length = 12; // Increased length for added security
    int num_passwords = 100;
    char passwords[num_passwords][password_length + 1];
    char used_hashes[num_passwords][HASH_SIZE] = { "\0" };

    for (int i = 0; i < num_passwords; ) {
        generate_password(passwords[i], password_length);

        char hash[HASH_SIZE];
        calculate_sha256(passwords[i], hash);

        // Check for duplicates using the hash
        int is_duplicate = 0;
        for (int j = 0; j < i; j++) {
            if (strcmp(used_hashes[j], hash) == 0) {
                is_duplicate = 1;
                break;
            }
        }

        if (!is_duplicate) {
            strncpy(used_hashes[i], hash, HASH_SIZE - 1);
            used_hashes[i][HASH_SIZE - 1] = '\0'; // Ensure null-termination here
            i++;
        }
    }

    // Print the passwords
    for (int i = 0; i < num_passwords; i++) {
        printf("Password %d: %s\n", i + 1, passwords[i]);
    }

    return 0;
}
