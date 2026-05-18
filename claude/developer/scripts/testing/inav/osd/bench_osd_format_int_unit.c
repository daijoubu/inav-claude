/*
 * bench_osd_format_int_unit.c
 *
 * Benchmarks three approaches to the common OSD pattern:
 *   tfp_sprintf(buff, "%3d%c", value, unit_sym)
 *
 * Approach 1: tfp_sprintf with "%Nd%c" format string (baseline)
 *   Full chain: tfp_sprintf -> va_start -> tfp_vsprintf -> tfp_vsnprintf
 *               -> tfp_nformat (format parse loop, putchw, per-char putcp
 *               function pointer calls) -> null terminator
 *
 * Approach 2: i2a + strlen + space-pad + strcpy + append unit
 *
 * Approach 3: i2a + strlen + space-pad + manual char copy (no strcpy) + append unit
 *
 * The i2a/ui2a/putchw/tfp_nformat implementations are copied verbatim from
 * inav2/src/main/common/typeconversion.c and printf.c so we measure the real
 * embedded code, not a libc proxy.
 *
 * Build:
 *   gcc -Os -o bench_osd_format_int_unit bench_osd_format_int_unit.c && \
 *   ./bench_osd_format_int_unit
 *
 * Build with O0 to see worst-case (no inlining):
 *   gcc -O0 -o bench_osd_format_int_unit bench_osd_format_int_unit.c && \
 *   ./bench_osd_format_int_unit
 */

#include <stdarg.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stddef.h>

/* -------------------------------------------------------------------------
 * Implementations copied verbatim from inav2 source
 * (typeconversion.c and printf.c)
 * ---------------------------------------------------------------------- */

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
    if (n < 0) {
        pr = 1;
        n = -n;
    }
    char ch;
    char *p = bf;
    while (*p++ && n > 0)
        n--;
    if (pr == 0) {
        while (n-- > 0) {
            if (putp < end) {
                putf(putp, fc);
            }
            written++;
        }
    }
    while ((ch = *bf++)) {
        if (putp < end) {
            putf(putp, ch);
        }
        written++;
    }
    if (pr == 1) {
        while (n-- > 0) {
            if (putp < end) {
                putf(putp, fc);
            }
            written++;
        }
    }
    return written;
}

/* a2i: parse decimal digits from *src into *nump, return next char */
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
    /*
     * On the target (32-bit ARM), UINT32_MAX is above all valid addresses so
     * it works as a "no limit" sentinel. On a 64-bit host, stack pointers are
     * above 0xFFFFFFFF, so we use UINTPTR_MAX instead.
     */
    const void *end = size < 0 ? (void *)(uintptr_t)UINTPTR_MAX
                               : ((char *)putp + size - 1);

    while ((ch = *(fmt++))) {
        if (ch != '%') {
            if (putp < end) {
                putf(putp, ch);
            }
            written++;
        } else {
            char lz = 0;
            char pr = 0;
            int w = 0;
            ch = *(fmt++);
            if (ch == '-') {
                ch = *(fmt++);
                pr = 1;
            }
            if (ch == '0') {
                ch = *(fmt++);
                lz = 1;
            }
            if (ch >= '0' && ch <= '9') {
                ch = a2i(ch, &fmt, 10, &w);
                if (pr) {
                    w = -w;
                }
            }
            switch (ch) {
            case 0:
                goto abort;
            case 'u':
                ui2a(va_arg(va, unsigned int), 10, 0, bf);
                written += putchw(putp, end, putf, w, lz, bf);
                break;
            case 'd':
                i2a(va_arg(va, int), bf);
                written += putchw(putp, end, putf, w, lz, bf);
                break;
            case 'c':
                if (putp < end) {
                    putf(putp, (char)(va_arg(va, int)));
                }
                written++;
                break;
            case 's':
                written += putchw(putp, end, putf, w, 0, va_arg(va, char *));
                break;
            case '%':
                if (putp < end) {
                    putf(putp, ch);
                }
                written++;
                break;
            default:
                break;
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

static int tfp_vsprintf(char *s, const char *fmt, va_list va)
{
    return tfp_vsnprintf(s, -1, fmt, va);
}

static int tfp_sprintf(char *s, const char *fmt, ...)
{
    va_list va;
    va_start(va, fmt);
    int written = tfp_vsprintf(s, fmt, va);
    va_end(va);
    return written;
}

/* -------------------------------------------------------------------------
 * Candidate implementations
 * ---------------------------------------------------------------------- */

/*
 * i2a_len: like i2a, but returns the number of characters written.
 * Eliminates the need for a separate strlen() call after i2a().
 * Declared static inline so it is always inlined into the macro below.
 *
 * Note: does not handle INT_MIN correctly (same limitation as i2a).
 */
static inline int i2a_len(int num, char *bf)
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
 * OSD_FORMAT_INT_UNIT macro
 *
 * Expands inline (guaranteed — no function call) and uses i2a_len to
 * count digits in a single pass, eliminating the strlen() call.
 *
 * Buffer overflow safety: same as the function variants — buff must hold
 * at least MAX(width, digits_in_value) + 2 bytes. The underscore-prefixed
 * locals avoid clashing with names in the surrounding scope.
 */
#define OSD_FORMAT_INT_UNIT(buff, width, value, unit) do {  \
    char _tmp[12];                                           \
    int _len = i2a_len((int)(value), _tmp);                 \
    int _pad = (width) - _len;                              \
    int _i = 0;                                              \
    while (_pad-- > 0) (buff)[_i++] = ' ';                  \
    const char *_src = _tmp;                                 \
    while (*_src) (buff)[_i++] = *_src++;                   \
    (buff)[_i++] = (unit);                                   \
    (buff)[_i]   = '\0';                                     \
} while (0)

/*
 * osdFormatIntUnit_strcpy
 *
 * Formats value right-justified to 'width' characters, followed by 'unit'.
 * Uses i2a + strcpy.
 *
 * Buffer overflow safety:
 *   buff must be at least MAX(width, digits_in_value) + 2 bytes.
 *   digits_in_value for INT_MAX (2147483647) is 10. In OSD code buffers are
 *   typically 32 bytes so this is safe for all realistic values and widths.
 *   If value has more digits than width, no padding is added (no truncation).
 */
static void osdFormatIntUnit_strcpy(char *buff, int width, int value, char unit)
{
    char tmp[12]; /* enough for -2147483648 + null */
    i2a(value, tmp);
    int len = (int)strlen(tmp);
    int pad = width - len;
    int i = 0;
    while (pad-- > 0) buff[i++] = ' ';
    strcpy(buff + i, tmp);
    i += len;
    buff[i++] = unit;
    buff[i]   = '\0';
}

/*
 * osdFormatIntUnit_direct
 *
 * Same as above but manually copies digits instead of calling strcpy,
 * saving the function call overhead and second strlen inside strcpy.
 *
 * Same buffer overflow safety as osdFormatIntUnit_strcpy.
 */
static void osdFormatIntUnit_direct(char *buff, int width, int value, char unit)
{
    char tmp[12];
    i2a(value, tmp);
    int len = (int)strlen(tmp);
    int pad = width - len;
    int i = 0;
    while (pad-- > 0) buff[i++] = ' ';
    const char *src = tmp;
    while (*src) buff[i++] = *src++;
    buff[i++] = unit;
    buff[i]   = '\0';
}

/*
 * osdFormatIntUnit_func
 *
 * Regular function (not macro), but uses i2a_len to avoid strlen.
 * Small code footprint: just one function (~50 bytes) plus i2a_len (~93 bytes).
 * The 9 call sites stay as regular function calls — no inline expansion.
 */
static void osdFormatIntUnit_func(char *buff, int width, int value, char unit)
{
    char tmp[12];
    int len = i2a_len(value, tmp);
    int pad = width - len;
    int i = 0;
    while (pad-- > 0) buff[i++] = ' ';
    const char *src = tmp;
    while (*src) buff[i++] = *src++;
    buff[i++] = unit;
    buff[i]   = '\0';
}

/* -------------------------------------------------------------------------
 * Benchmark harness
 * ---------------------------------------------------------------------- */

#define ITERATIONS 10000000

static double elapsed_ms(struct timespec start, struct timespec end)
{
    return (end.tv_sec - start.tv_sec) * 1000.0
         + (end.tv_nsec - start.tv_nsec) / 1e6;
}

/* Use volatile sink to prevent the compiler optimising away the calls */
static volatile char sink;

static void burn_sprintf(int width, const int *values, int nvalues, char unit,
                         char *fmt)
{
    char buff[32];
    for (int i = 0; i < ITERATIONS; i++) {
        tfp_sprintf(buff, fmt, values[i % nvalues], (int)unit);
        sink = buff[0];
    }
}

static void burn_strcpy(int width, const int *values, int nvalues, char unit)
{
    char buff[32];
    for (int i = 0; i < ITERATIONS; i++) {
        osdFormatIntUnit_strcpy(buff, width, values[i % nvalues], unit);
        sink = buff[0];
    }
}

static void burn_direct(int width, const int *values, int nvalues, char unit)
{
    char buff[32];
    for (int i = 0; i < ITERATIONS; i++) {
        osdFormatIntUnit_direct(buff, width, values[i % nvalues], unit);
        sink = buff[0];
    }
}

static void burn_func(int width, const int *values, int nvalues, char unit)
{
    char buff[32];
    for (int i = 0; i < ITERATIONS; i++) {
        osdFormatIntUnit_func(buff, width, values[i % nvalues], unit);
        sink = buff[0];
    }
}

static void burn_macro(int width, const int *values, int nvalues, char unit)
{
    char buff[32];
    for (int i = 0; i < ITERATIONS; i++) {
        OSD_FORMAT_INT_UNIT(buff, width, values[i % nvalues], unit);
        sink = buff[0];
    }
}

/* -------------------------------------------------------------------------
 * Correctness check
 * ---------------------------------------------------------------------- */

static void check(int width, int value, char unit, const char *fmt)
{
    char ref[32], r2[32], r3[32], r4[32];
    tfp_sprintf(ref, fmt, value, (int)unit);
    osdFormatIntUnit_strcpy(r2, width, value, unit);
    osdFormatIntUnit_direct(r3, width, value, unit);
    OSD_FORMAT_INT_UNIT(r4, width, value, unit);

    char r5[32];
    osdFormatIntUnit_func(r5, width, value, unit);

    int ok = (strcmp(ref, r2) == 0) && (strcmp(ref, r3) == 0)
          && (strcmp(ref, r4) == 0) && (strcmp(ref, r5) == 0);
    printf("  width=%d value=%-12d ref=\"%s\"  func=\"%s\"  macro=\"%s\"  %s\n",
           width, value, ref, r5, r4, ok ? "OK" : "MISMATCH!");
    if (!ok) exit(1);
}

/* -------------------------------------------------------------------------
 * main
 * ---------------------------------------------------------------------- */

int main(void)
{
    /* --- correctness --- */
    printf("Correctness checks:\n");

    /* width=3 (most common in osd.c) */
    check(3,   0,   'k', "%3d%c");
    check(3,   7,   'k', "%3d%c");
    check(3,  42,   'k', "%3d%c");
    check(3, 100,   'k', "%3d%c");
    check(3, 999,   'k', "%3d%c");
    check(3,  -5,   'k', "%3d%c");

    /* value wider than field — no truncation, just no padding */
    check(3, 12345, 'k', "%3d%c");

    /* other widths seen in osd.c */
    check(2,  15,   'm', "%2d%c");
    check(4, 1234,  'f', "%4d%c");
    check(5, 99999, 'f', "%5d%c");

    printf("\n");

    /* --- benchmark --- */
    /* Mix of values that exercise different digit counts */
    const int values[] = { 0, 7, 42, 100, 999, -5, 3600, 12345 };
    const int nvalues  = sizeof(values) / sizeof(values[0]);
    const int width    = 3;
    const char unit    = 'k';
    char fmt[]         = "%3d%c";

    struct timespec t0, t1;

    printf("Benchmark: %d iterations each, width=%d, mixed values\n\n",
           ITERATIONS, width);

    clock_gettime(CLOCK_MONOTONIC, &t0);
    burn_sprintf(width, values, nvalues, unit, fmt);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double ms_sprintf = elapsed_ms(t0, t1);

    clock_gettime(CLOCK_MONOTONIC, &t0);
    burn_strcpy(width, values, nvalues, unit);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double ms_strcpy = elapsed_ms(t0, t1);

    clock_gettime(CLOCK_MONOTONIC, &t0);
    burn_direct(width, values, nvalues, unit);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double ms_direct = elapsed_ms(t0, t1);

    clock_gettime(CLOCK_MONOTONIC, &t0);
    burn_func(width, values, nvalues, unit);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double ms_func = elapsed_ms(t0, t1);

    clock_gettime(CLOCK_MONOTONIC, &t0);
    burn_macro(width, values, nvalues, unit);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double ms_macro = elapsed_ms(t0, t1);

    printf("  tfp_sprintf (\"%s\"):        %7.1f ms  (%5.2f ns/call)  1.00x (baseline)\n",
           fmt, ms_sprintf, ms_sprintf * 1e6 / ITERATIONS);
    printf("  func  (i2a+strlen+copy):   %7.1f ms  (%5.2f ns/call)  %.2fx\n",
           ms_strcpy, ms_strcpy * 1e6 / ITERATIONS, ms_sprintf / ms_strcpy);
    printf("  func  (i2a+strlen+nocpy):  %7.1f ms  (%5.2f ns/call)  %.2fx\n",
           ms_direct, ms_direct * 1e6 / ITERATIONS, ms_sprintf / ms_direct);
    printf("  func  (i2a_len, no strlen):%7.1f ms  (%5.2f ns/call)  %.2fx\n",
           ms_func, ms_func * 1e6 / ITERATIONS, ms_sprintf / ms_func);
    printf("  macro (i2a_len, inline):   %7.1f ms  (%5.2f ns/call)  %.2fx\n",
           ms_macro, ms_macro * 1e6 / ITERATIONS, ms_sprintf / ms_macro);

    return 0;
}
