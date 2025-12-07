#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *generate_password() {
    static char password[9];
    for (int i = 0; i < 8; ++i) {
        password[i] = 'A' + (rand() % 26);
    }
    password[8] = '\0';
    return password;
}

int main() {
    srand(time(NULL));
    printf("%s\n", generate_password());
    return 0;
}
