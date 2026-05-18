/*
 * bench_osd_patterns.c
 *
 * Benchmarks the top 5 tfp_sprintf patterns found in osd.c against
 * dedicated replacements.
 *
 * Pattern 1: "%Nd"      — padded int, no unit        (21 call sites)
 * Pattern 2: "%c%c"     — two symbol chars            (~10 call sites)
 * Pattern 3: "%c"       — one symbol char             (~8 call sites)
 * Pattern 4: "%Nd%c"    — padded int + unit           (9 call sites)
 * Pattern 5: "%02d:%02d"— MM:SS time                  (4 call sites)
 *
 * All tfp_sprintf / i2a / ui2a / putchw / tfp_nformat code is copied
 * verbatim from inav2/src/main/common/{printf.c,typeconversion.c} so
 * we measure the real embedded implementation.
 *
 * Build:
 *   gcc -Os -o bench_osd_patterns bench_osd_patterns.c && ./bench_osd_patterns
 */

#include <stdarg.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stddef.h>

/* =========================================================================
 * Verbatim INAV implementations (typeconversion.c + printf.c)
 * ======================================================================= */

static void ui2a(unsigned int num, unsigned int base, int uc, char *bf)
{
    int n = 0;
    unsigned int d = 1;
    while (num / d >= base)
        d *= base;
    while (d != 0) {
        int dgt = num / d;
        num %= d;
        d /= base;
        if (n || dgt > 0 || d == 0) {
            *bf++ = dgt + (dgt < 10 ? '0' : (uc ? 'A' : 'a') - 10);
            ++n;
        }
    }
    *bf = 0;
}

static void i2a(int num, char *bf)
{
    if (num < 0) {
        num = -num;
        *bf++ = '-';
    }
    ui2a(num, 10, 0, bf);
}

typedef void (*putcf)(void *, char);

static int putchw(void *putp, const void *end, putcf putf, int n, char z, char *bf)
{
    int written = 0;
    char fc = z ? '0' : ' ';
    char pr = 0;
    if (n < 0) { pr = 1; n = -n; }
    char ch;
    char *p = bf;
    while (*p++ && n > 0) n--;
    if (pr == 0) {
        while (n-- > 0) { if (putp < end) putf(putp, fc); written++; }
    }
    while ((ch = *bf++)) { if (putp < end) putf(putp, ch); written++; }
    if (pr == 1) {
        while (n-- > 0) { if (putp < end) putf(putp, fc); written++; }
    }
    return written;
}

static char a2i(char ch, const char **src, int base, int *nump)
{
    int num = 0;
    while (ch >= '0' && ch <= '9') {
        num = num * base + (ch - '0');
        ch = *((*src)++);
    }
    *nump = num;
    return ch;
}

static void putcp(void *p, char c)
{
    *(*((char **) p))++ = c;
}

static int tfp_nformat(void *putp, int size, void (*putf)(void *, char),
                       const char *fmt, va_list va)
{
    char bf[12];
    int written = 0;
    char ch;
    const void *end = size < 0 ? (void *)(uintptr_t)UINTPTR_MAX
                               : ((char *)putp + size - 1);

    while ((ch = *(fmt++))) {
        if (ch != '%') {
            if (putp < end) putf(putp, ch);
            written++;
        } else {
            char lz = 0;
            char pr = 0;
            int w = 0;
            ch = *(fmt++);
            if (ch == '-') { ch = *(fmt++); pr = 1; }
            if (ch == '0') { ch = *(fmt++); lz = 1; }
            if (ch >= '0' && ch <= '9') {
                ch = a2i(ch, &fmt, 10, &w);
                if (pr) w = -w;
            }
            switch (ch) {
            case 0: goto abort;
            case 'u': ui2a(va_arg(va, unsigned int), 10, 0, bf);
                      written += putchw(putp, end, putf, w, lz, bf); break;
            case 'd': i2a(va_arg(va, int), bf);
                      written += putchw(putp, end, putf, w, lz, bf); break;
            case 'c': if (putp < end) putf(putp, (char)(va_arg(va, int)));
                      written++; break;
            case 's': written += putchw(putp, end, putf, w, 0, va_arg(va, char *)); break;
            case '%': if (putp < end) putf(putp, ch); written++; break;
            default: break;
            }
        }
    }
abort:
    return written;
}

static int tfp_vsnprintf(char *s, int size, const char *fmt, va_list va)
{
    int written = tfp_nformat(&s, size, putcp, fmt, va);
    putcp(&s, 0);
    return written;
}

static int tfp_sprintf(char *s, const char *fmt, ...)
{
    va_list va;
    va_start(va, fmt);
    int written = tfp_vsnprintf(s, -1, fmt, va);
    va_end(va);
    return written;
}

/* =========================================================================
 * Optimized replacements
 * ======================================================================= */

/*
 * i2a_len: converts int to string, returns length written.
 * Single pass — no strlen needed afterward.
 */
static int i2a_len(int num, char *bf)
{
    char *start = bf;
    if (num < 0) {
        num = -num;
        *bf++ = '-';
    }
    unsigned int u = (unsigned int)num;
    unsigned int d = 1;
    while (u / d >= 10)
        d *= 10;
    while (d != 0) {
        unsigned int dgt = u / d;
        u %= d;
        d /= 10;
        *bf++ = '0' + dgt;
    }
    *bf = '\0';
    return (int)(bf - start);
}

/*
 * Pattern 1: "%Nd" — padded int, no unit
 * Replaces: tfp_sprintf(buff, "%3d", value)
 * buff must hold at least max(width, digits) + 1 bytes.
 */
static void osdFormatInt(char *buff, int width, int value)
{
    char tmp[12];
    int len = i2a_len(value, tmp);
    int pad = width - len;
    int i = 0;
    while (pad-- > 0) buff[i++] = ' ';
    const char *src = tmp;
    while (*src) buff[i++] = *src++;
    buff[i] = '\0';
}

/*
 * Pattern 4: "%Nd%c" — padded int + unit char
 * Replaces: tfp_sprintf(buff, "%3d%c", value, unit)
 * buff must hold at least max(width, digits) + 2 bytes.
 */
static void osdFormatIntUnit(char *buff, int width, int value, char unit)
{
    char tmp[12];
    int len = i2a_len(value, tmp);
    int pad = width - len;
    int i = 0;
    while (pad-- > 0) buff[i++] = ' ';
    const char *src = tmp;
    while (*src) buff[i++] = *src++;
    buff[i++] = unit;
    buff[i] = '\0';
}

/*
 * Pattern 5: "%02d:%02d" — MM:SS time format
 * Replaces: tfp_sprintf(buff, "%02d:%02d", minutes, seconds)
 * buff must hold at least 6 bytes.
 * Values are expected 0..99; no bounds check.
 */
static void osdFormatTime(char *buff, int m, int s)
{
    buff[0] = '0' + m / 10;
    buff[1] = '0' + m % 10;
    buff[2] = ':';
    buff[3] = '0' + s / 10;
    buff[4] = '0' + s % 10;
    buff[5] = '\0';
}

/* =========================================================================
 * Benchmark harness
 * ======================================================================= */

#define ITERATIONS 10000000

static double elapsed_ms(struct timespec start, struct timespec end)
{
    return (end.tv_sec - start.tv_sec) * 1000.0
         + (end.tv_nsec - start.tv_nsec) / 1e6;
}

static volatile char sink;

/* =========================================================================
 * Correctness checks
 * ======================================================================= */

static void check_equal(const char *label, const char *ref, const char *opt)
{
    int ok = (strcmp(ref, opt) == 0);
    printf("  %-28s ref=%-12s opt=%-12s %s\n", label, ref, opt,
           ok ? "OK" : "MISMATCH!");
    if (!ok) exit(1);
}

static void correctness_checks(void)
{
    char ref[32], opt[32];

    printf("Correctness checks:\n");

    /* Pattern 1: "%Nd" */
    tfp_sprintf(ref, "%3d", 0);    osdFormatInt(opt, 3, 0);    check_equal("%%3d val=0", ref, opt);
    tfp_sprintf(ref, "%3d", 42);   osdFormatInt(opt, 3, 42);   check_equal("%%3d val=42", ref, opt);
    tfp_sprintf(ref, "%3d", -7);   osdFormatInt(opt, 3, -7);   check_equal("%%3d val=-7", ref, opt);
    tfp_sprintf(ref, "%5d", 99999);osdFormatInt(opt, 5, 99999);check_equal("%%5d val=99999", ref, opt);
    tfp_sprintf(ref, "%3d", 9999); osdFormatInt(opt, 3, 9999); check_equal("%%3d val=9999 (overflow)", ref, opt);

    /* Pattern 2: "%c%c" */
    tfp_sprintf(ref, "%c%c", 'A', 'B');
    opt[0] = 'A'; opt[1] = 'B'; opt[2] = '\0';
    check_equal("%%c%%c AB", ref, opt);

    /* Pattern 3: "%c" */
    tfp_sprintf(ref, "%c", 'X');
    opt[0] = 'X'; opt[1] = '\0';
    check_equal("%%c X", ref, opt);

    /* Pattern 4: "%Nd%c" */
    tfp_sprintf(ref, "%3d%c", 42, 'k');  osdFormatIntUnit(opt, 3, 42, 'k');  check_equal("%%3d%%c val=42 k", ref, opt);
    tfp_sprintf(ref, "%4d%c", -15, 'D'); osdFormatIntUnit(opt, 4, -15, 'D'); check_equal("%%4d%%c val=-15 D", ref, opt);

    /* Pattern 5: "%02d:%02d" */
    tfp_sprintf(ref, "%02d:%02d", 3, 7);   osdFormatTime(opt, 3, 7);   check_equal("%%02d:%%02d 3:7", ref, opt);
    tfp_sprintf(ref, "%02d:%02d", 59, 59); osdFormatTime(opt, 59, 59); check_equal("%%02d:%%02d 59:59", ref, opt);
    tfp_sprintf(ref, "%02d:%02d", 0, 0);   osdFormatTime(opt, 0, 0);   check_equal("%%02d:%%02d 0:0", ref, opt);

    printf("\n");
}

/* =========================================================================
 * Benchmark runners
 * ======================================================================= */

static void bench_pattern(const char *name, int calls_in_osd,
                          double ms_old, double ms_new)
{
    double pct = (ms_old - ms_new) / ms_old * 100.0;
    printf("  %-22s %7.1f ms -> %7.1f ms  (%4.1f%% faster)  %d call sites\n",
           name, ms_old, ms_new, pct, calls_in_osd);
}

int main(void)
{
    correctness_checks();

    const int values[] = { 0, 7, 42, 100, 255, -5, 999, 3600 };
    const int nvalues = sizeof(values) / sizeof(values[0]);

    struct timespec t0, t1;
    char buff[32];

    printf("Benchmark: %d iterations each, -Os\n\n", ITERATIONS);

    /* --- Pattern 1: "%Nd" (21 call sites) --- */
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < ITERATIONS; i++) {
        tfp_sprintf(buff, "%3d", values[i % nvalues]);
        sink = buff[0];
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double p1_old = elapsed_ms(t0, t1);

    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < ITERATIONS; i++) {
        osdFormatInt(buff, 3, values[i % nvalues]);
        sink = buff[0];
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double p1_new = elapsed_ms(t0, t1);

    /* --- Pattern 2: "%c%c" (~10 call sites) --- */
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < ITERATIONS; i++) {
        tfp_sprintf(buff, "%c%c", 'A' + (i & 7), 'a' + (i & 7));
        sink = buff[0];
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double p2_old = elapsed_ms(t0, t1);

    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < ITERATIONS; i++) {
        buff[0] = 'A' + (i & 7);
        buff[1] = 'a' + (i & 7);
        buff[2] = '\0';
        sink = buff[0];
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double p2_new = elapsed_ms(t0, t1);

    /* --- Pattern 3: "%c" (~8 call sites) --- */
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < ITERATIONS; i++) {
        tfp_sprintf(buff, "%c", 'A' + (i & 7));
        sink = buff[0];
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double p3_old = elapsed_ms(t0, t1);

    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < ITERATIONS; i++) {
        buff[0] = 'A' + (i & 7);
        buff[1] = '\0';
        sink = buff[0];
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double p3_new = elapsed_ms(t0, t1);

    /* --- Pattern 4: "%Nd%c" (9 call sites) --- */
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < ITERATIONS; i++) {
        tfp_sprintf(buff, "%3d%c", values[i % nvalues], (int)'k');
        sink = buff[0];
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double p4_old = elapsed_ms(t0, t1);

    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < ITERATIONS; i++) {
        osdFormatIntUnit(buff, 3, values[i % nvalues], 'k');
        sink = buff[0];
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double p4_new = elapsed_ms(t0, t1);

    /* --- Pattern 5: "%02d:%02d" (4 call sites) --- */
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < ITERATIONS; i++) {
        int m = values[i % nvalues] % 60;
        int s = values[(i+1) % nvalues] % 60;
        tfp_sprintf(buff, "%02d:%02d", m, s);
        sink = buff[0];
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double p5_old = elapsed_ms(t0, t1);

    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < ITERATIONS; i++) {
        int m = values[i % nvalues] % 60;
        int s = values[(i+1) % nvalues] % 60;
        osdFormatTime(buff, m, s);
        sink = buff[0];
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double p5_new = elapsed_ms(t0, t1);

    /* --- Results --- */
    bench_pattern("1. \"%Nd\" (int)",      21, p1_old, p1_new);
    bench_pattern("2. \"%c%c\" (2 sym)",   10, p2_old, p2_new);
    bench_pattern("3. \"%c\" (1 sym)",       8, p3_old, p3_new);
    bench_pattern("4. \"%Nd%c\" (int+unit)", 9, p4_old, p4_new);
    bench_pattern("5. \"%02d:%02d\" (time)", 4, p5_old, p5_new);

    /* --- Weighted estimate --- */
    printf("\n  Weighted total per OSD refresh (all %d call sites):\n",
           21 + 10 + 8 + 9 + 4);
    double ns_per = 1e6 / ITERATIONS;  /* convert ms to ns per call */
    double old_total = 21*p1_old + 10*p2_old + 8*p3_old + 9*p4_old + 4*p5_old;
    double new_total = 21*p1_new + 10*p2_new + 8*p3_new + 9*p4_new + 4*p5_new;
    double pct_total = (old_total - new_total) / old_total * 100.0;
    printf("    old: %.0f ns   new: %.0f ns   saved: %.0f ns  (%.1f%% faster)\n",
           old_total * ns_per, new_total * ns_per,
           (old_total - new_total) * ns_per, pct_total);

    return 0;
}
