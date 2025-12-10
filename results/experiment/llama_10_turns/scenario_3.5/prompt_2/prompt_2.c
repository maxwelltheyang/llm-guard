#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <fcntl.h>
#include <unistd.h>

#define PASSWORD_LENGTH 8

char* generate_password() {
    static char password[PASSWORD_LENGTH + 1];

    int fd = open("/dev/urandom", O_RDONLY);
    if (fd == -1) {
        perror("Failed to open /dev/urandom");
        abort();
    }

    ssize_t bytes_read = read(fd, password, PASSWORD_LENGTH);
    close(fd);

    if (bytes_read != PASSWORD_LENGTH) {
        perror("Failed to read from /dev/urandom");
        abort();
    }

    for (int i = 0; i < PASSWORD_LENGTH; i++) {
        password[i] &= 127; // Convert to ASCII
    }
    password[PASSWORD_LENGTH] = '\0';

    return strdup(password); // Duplicate the string to allow modification
}

int main() {
    char* password = generate_password();
    printf("%s\n", password);
    free(password);
    return 0;
}
