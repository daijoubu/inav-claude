# GDB script using memory addresses for breakpoints

set pagination off
set logging on
set logging file /tmp/gdb_timing.log

# Connect to OpenOCD
target extended-remote localhost:3333

# Small delay for connection
shell sleep 1

echo "Connected. Setting breakpoints by address...\n"

# Set breakpoints using memory addresses (from nm output)
break *0x08018344
break *0x08018434

echo "Breakpoints set. Continuing...\n"

# Continue and let it run
continue
