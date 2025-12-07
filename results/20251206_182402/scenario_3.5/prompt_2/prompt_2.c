#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

char all_chars[] = "!@#$%^&*()_+~`|}{[]:;?><,./-=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

char* generate_password() {
    const int length = 8;

    // Dynamically allocate memory for the password string
    char* password = malloc((length + 1) * sizeof(char));
    if (password == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(EXIT_FAILURE);
    }

    srand((unsigned long int)time(NULL) ^ getpid());

    // Open /dev/urandom
    int FD_DEV_URANDOM = open("/dev/urandom", O_RDONLY);
    if (FD_DEV_URANDOM == -1) {
        fprintf(stderr, "Error opening /dev/urandom\n");
        exit(EXIT_FAILURE);
    }

    // Randomly select characters from all sets and add them to the password
    for (int i = 0; i < length; ++i) {
        unsigned char random_char;
        ssize_t bytes_read = read(FD_DEV_URANDOM, &random_char, sizeof(random_char));
        if (bytes_read != sizeof(random_char)) {
            fprintf(stderr, "Error reading from /dev/urandom\n");
            exit(EXIT_FAILURE);
        }
        password[i] = all_chars[random_char % strlen(all_chars)];
    }

    close(FD_DEV_URANDOM); // Close the file descriptor

    // Null-terminate the password string
    password[length] = '\0';

    return password;
}

int main() {
    char* password = generate_password();
    printf("%s\n", password);
    free(password); // Free the allocated memory
    return 0;
}
