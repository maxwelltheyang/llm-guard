#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/rand.h>

#define PASSWORD_LENGTH 8

char* generate_password() {
    static char password[PASSWORD_LENGTH + 1];

    if (RAND_bytes((unsigned char*)password, PASSWORD_LENGTH) != 1) {
        fprintf(stderr, "Failed to generate random bytes\n");
        exit(1);
    }
    password[PASSWORD_LENGTH] = '\0';

    return strdup(password);
}

int main() {
    char* password = generate_password();
    if (password == NULL) {
        fprintf(stderr, "Failed to duplicate string\n");
        exit(1);
    }
    printf("%s\n", password);
    free(password);
    return 0;
}
