# GDB script for measuring SD card blocking times
# This version uses GDB commands instead of Python (which may not be available)

# Set up GDB for remote debugging
set pagination off
set logging on
set logging file /tmp/gdb_timing.log

# Connect to OpenOCD
target extended-remote localhost:3333

echo "Connected to target. Setting breakpoints...\n"

# Set breakpoints at INAV SD card functions
# These may be static/local functions, so try with file context
break sdcard_sdio.c:sdcardSdio_init
break sdcard_sdio.c:sdcardSdio_poll
break blackbox.c:blackboxStart

echo "Breakpoints set. Continuing execution...\n"

# Continue running
continue

# The script ends here - GDB will continue and log breakpoint hits to the log file
