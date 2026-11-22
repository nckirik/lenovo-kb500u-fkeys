#include <X11/Xlib.h>
#include <X11/keysym.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static Display *open_display(void) {
    const char *name = getenv("DISPLAY");
    Display *d = XOpenDisplay(name);
    if (!d) {
        fprintf(stderr, "x11-keymap: cannot open display %s\n", name ? name : "(unset)");
        exit(1);
    }
    return d;
}

static void dump(Display *d) {
    int min, max, per;
    XDisplayKeycodes(d, &min, &max);
    KeySym *syms = XGetKeyboardMapping(d, min, max - min + 1, &per);
    if (!syms) {
        fprintf(stderr, "x11-keymap: XGetKeyboardMapping failed\n");
        exit(1);
    }
    for (int k = min; k <= max; k++) {
        printf("keycode %3d", k);
        int printed = 0;
        for (int j = 0; j < per; j++) {
            KeySym s = syms[(k - min) * per + j];
            if (s != NoSymbol) {
                printf(" %s", XKeysymToString(s));
                printed = 1;
            }
        }
        if (!printed) printf(" (none)");
        printf("\n");
    }
    XFree(syms);
}

static int parse_keycode(const char *token) {
    char *end = NULL;
    long value = strtol(token, &end, 0);
    if (!end || *end || value < 8 || value > 255) return -1;
    return (int)value;
}

static int x_error_seen = 0;

static int x_error(Display *d, XErrorEvent *e) {
    char text[256];
    XGetErrorText(d, e->error_code, text, sizeof(text));
    fprintf(stderr, "x11-keymap: X error: %s (request %d.%d)\n",
            text, e->request_code, e->minor_code);
    x_error_seen = 1;
    return 0;
}

static void apply_key(Display *d, int keycode, char **symbols, int count) {
    if (count < 1 || count > 8) {
        fprintf(stderr, "x11-keymap: keycode %d needs 1-8 keysyms\n", keycode);
        exit(1);
    }
    KeySym wanted[8] = {0};
    for (int i = 0; i < count; i++) {
        wanted[i] = XStringToKeysym(symbols[i]);
        if (wanted[i] == NoSymbol) {
            fprintf(stderr, "x11-keymap: unknown keysym '%s'\n", symbols[i]);
            exit(1);
        }
    }

    int per = 0;
    KeySym *old = XGetKeyboardMapping(d, keycode, 1, &per);
    if (!old || per < 1) {
        fprintf(stderr, "x11-keymap: cannot read current mapping for keycode %d\n", keycode);
        exit(1);
    }
    KeySym *syms = calloc((size_t)per, sizeof(KeySym));
    if (!syms) {
        fprintf(stderr, "x11-keymap: out of memory\n");
        exit(1);
    }
    for (int i = 0; i < per; i++) {
        syms[i] = (i < count) ? wanted[i] : wanted[count - 1];
    }

    XSetErrorHandler(x_error);
    x_error_seen = 0;
    XChangeKeyboardMapping(d, keycode, per, syms, 1);
    XSync(d, False);
    free(syms);
    XFree(old);

    /* XChangeKeyboardMapping() returns 0 even on success on Termux:X11.
     * Verify by reading the mapping back instead. */
    int ok = 0;
    if (!x_error_seen) {
        int check_per = 0;
        KeySym *check = XGetKeyboardMapping(d, keycode, 1, &check_per);
        if (check && check_per >= count) {
            ok = 1;
            for (int i = 0; i < count; i++) {
                if (check[i] != wanted[i]) {
                    ok = 0;
                    break;
                }
            }
        }
        if (check) XFree(check);
    }
    if (!ok) {
        fprintf(stderr, "x11-keymap: failed to update keycode %d\n", keycode);
        exit(1);
    }
}

static void apply_file(Display *d, const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) {
        perror(path);
        exit(1);
    }
    char line[512];
    int lineno = 0;
    while (fgets(line, sizeof(line), f)) {
        lineno++;
        char *hash = strchr(line, '#');
        if (hash) *hash = '\0';
        char *save = NULL;
        char *token = strtok_r(line, " \t\r\n", &save);
        if (!token) continue;
        if (strcmp(token, "keycode") == 0) {
            token = strtok_r(NULL, " \t\r\n", &save);
            if (!token) {
                fprintf(stderr, "x11-keymap: line %d: missing keycode\n", lineno);
                exit(1);
            }
        }
        int keycode = parse_keycode(token);
        if (keycode < 0) {
            fprintf(stderr, "x11-keymap: line %d: bad keycode '%s'\n", lineno, token);
            exit(1);
        }
        token = strtok_r(NULL, " \t\r\n", &save);
        if (token && strcmp(token, "=") == 0) token = strtok_r(NULL, " \t\r\n", &save);
        char *symbols[8];
        int count = 0;
        while (token && count < 8) {
            symbols[count++] = token;
            token = strtok_r(NULL, " \t\r\n", &save);
        }
        if (!count) {
            fprintf(stderr, "x11-keymap: line %d: no keysyms\n", lineno);
            exit(1);
        }
        apply_key(d, keycode, symbols, count);
    }
    fclose(f);
    XSync(d, False);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s dump | apply <file> | hold <file> | set <keycode> <keysym>...\n", argv[0]);
        return 2;
    }
    Display *d = open_display();
    if (strcmp(argv[1], "dump") == 0) {
        dump(d);
    } else if (strcmp(argv[1], "apply") == 0 && argc >= 3) {
        apply_file(d, argv[2]);
        printf("x11-keymap: applied %s\n", argv[2]);
    } else if (strcmp(argv[1], "hold") == 0 && argc >= 3) {
        apply_file(d, argv[2]);
        printf("x11-keymap: holding %s\n", argv[2]);
        fflush(stdout);
        for (;;) pause();
    } else if (strcmp(argv[1], "set") == 0 && argc >= 4) {
        int keycode = parse_keycode(argv[2]);
        if (keycode < 0) {
            fprintf(stderr, "x11-keymap: bad keycode '%s'\n", argv[2]);
            return 2;
        }
        apply_key(d, keycode, &argv[3], argc - 3);
        XSync(d, False);
        printf("x11-keymap: keycode %d updated\n", keycode);
    } else {
        fprintf(stderr, "usage: %s dump | apply <file> | hold <file> | set <keycode> <keysym>...\n", argv[0]);
        return 2;
    }
    XCloseDisplay(d);
    return 0;
}
