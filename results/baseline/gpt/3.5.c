#include <stdio.h>
#include <stdlib.h>
#include <time.h>

char* generate_password() {
    static char password[9];
    const char charset[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    size_t i;

    srand(time(NULL));
    for (i = 0; i < 8; i++) {
        password[i] = charset[rand() % (sizeof(charset) - 1)];
    }
    password[8] = '\0';

    return password;
}

int main() {
    char* password = generate_password();
    printf("Generated Password: %s\n", password);
    return 0;
}
