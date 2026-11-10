/*
 * pwn1 -- classic stack buffer overflow, no mitigations that matter.
 *
 * Built with -fno-stack-protector and -no-pie (see Dockerfile) so the intended
 * primitive is a straight saved-return-address overwrite to win(). The flag is
 * read from the environment at runtime (FLAG), which is how the per-student
 * value is injected into that student's instance -- it is never in the binary.
 *
 * Difficulty: introductory. This is the "two trivially solvable" tier so nobody
 * scores zero. Add a bad char / alignment / ROP variant for the harder tier.
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/* gets() was removed from <stdio.h> in modern glibc but still exists in the
 * library; declare it so the build doesn't die on an implicit declaration.
 * It is the intended vulnerable primitive (unbounded read into name[64]). */
extern char *gets(char *);

void win(void) {
    char *flag = getenv("FLAG");
    if (!flag) flag = "flag{local-test-no-FLAG-in-env}";
    puts(flag);
    fflush(stdout);
    _exit(0);
}

void vuln(void) {
    char name[64];
    puts("What's your name?");
    fflush(stdout);
    /* the bug: gets() has no bound, name is 64 bytes */
    gets(name);
    printf("Hello, %s\n", name);
    fflush(stdout);
}

int main(void) {
    /* no buffering so it behaves the same over a socket */
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    vuln();
    puts("Goodbye.");
    return 0;
}
