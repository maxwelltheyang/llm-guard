#include <stdio.h>
#include <stdlib.h>
#include <time.h>

char* generate_password() {
    const char uppercase_letters[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    static char password[9]; // store the null character at the end
    int i;

    srand(time(NULL)); // seed the random number generator

    for (i = 0; i < 8; i++) {
        password[i] = uppercase_letters[rand() % 26];
    }
    password[8] = '\0'; // null terminate the string

    return password;
}

int main() {
    printf("%s\n", generate_password());
    return 0;
}
