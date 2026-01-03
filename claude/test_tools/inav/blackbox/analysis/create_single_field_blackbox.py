#!/usr/bin/env python3
"""
Create a minimal blackbox firmware that only logs loopIteration and time.
This helps isolate encoding issues by testing the simplest case.
"""

import re

BLACKBOX_C = "/home/raymorris/Documents/planes/inavflight/inav/src/main/blackbox/blackbox.c"

# Read the original file
with open(BLACKBOX_C, 'r') as f:
    content = f.read()

# 1. Replace blackboxMainFields[] array with only loopIteration and time
fields_pattern = r'(static const blackboxDeltaFieldDefinition_t blackboxMainFields\[\] = \{)[^}]+(^\};)'
fields_replacement = r'''\1
    /* SINGLE FIELD TEST - Only loopIteration and time */
    {"loopIteration",-1, UNSIGNED, .Ipredict = PREDICT(0),     .Iencode = ENCODING(UNSIGNED_VB), .Ppredict = PREDICT(INC),           .Pencode = FLIGHT_LOG_FIELD_ENCODING_NULL, CONDITION(ALWAYS)},
    {"time",       -1, UNSIGNED, .Ipredict = PREDICT(0),       .Iencode = ENCODING(UNSIGNED_VB), .Ppredict = PREDICT(STRAIGHT_LINE), .Pencode = ENCODING(SIGNED_VB), CONDITION(ALWAYS)},
\2'''

content = re.sub(fields_pattern, fields_replacement, content, flags=re.MULTILINE | re.DOTALL)

# 2. In writeIntraframe(), keep only loopIteration and time writes
# Find writeIntraframe function and wrap extra writes
intra_pattern = r'(blackboxWriteUnsignedVB\(blackboxCurrent->time\);)\s+(blackboxWriteSignedVBArray)'
intra_replacement = r'\1\n\n    /* SINGLE FIELD TEST - Skip all other field writes */\n    goto skip_intra_writes;\n    \2'
content = re.sub(intra_pattern, intra_replacement)

# Add label before history rotation in writeIntraframe
content = re.sub(
    r'(\s+)(//Rotate our history buffers:)',
    r'\1skip_intra_writes:\n\1\2',
    content
)

# 3. In writeInterframe(), keep only time delta write
inter_pattern = r'(blackboxWriteSignedVB\(\(int32_t\) \(blackboxHistory\[0\]->time[^;]+\);)\s+(int32_t deltas)'
inter_replacement = r'\1\n\n    /* SINGLE FIELD TEST - Skip all other field writes */\n    goto skip_inter_writes;\n    \2'
content = re.sub(inter_pattern, inter_replacement)

# Add label before history rotation in writeInterframe
content = re.sub(
    r'(\s+)(//Rotate our history buffers\s+blackboxHistory\[2\] = blackboxHistory)',
    r'\1skip_inter_writes:\n\1//Rotate our history buffers\n\1blackboxHistory[2] = blackboxHistory',
    content
)

# Write the modified file
with open(BLACKBOX_C, 'w') as f:
    f.write(content)

print("✓ Created single-field blackbox firmware")
print("  - Only loopIteration and time will be logged")
print("  - All other field writes skipped with goto")
