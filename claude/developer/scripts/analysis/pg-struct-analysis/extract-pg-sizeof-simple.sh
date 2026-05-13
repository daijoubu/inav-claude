#!/bin/bash
#
# Extract PG struct sizes using a simple compile test
# Doesn't require DWARF debug info
#

set -euo pipefail

STRUCT_TYPE=$1
TARGET=${2:-SITL}

echo "Getting sizeof($STRUCT_TYPE) for target $TARGET..." >&2

# Create temporary C file that outputs the size
cat > /tmp/sizeof_test.c << EOF
#include <stdio.h>
#include "platform.h"
#include "build/build_config.h"

// Include all common PG headers
#include "config/parameter_group.h"
#include "config/parameter_group_ids.h"
#include "blackbox/blackbox.h"
#include "sensors/battery.h"
#include "navigation/navigation.h"
#include "fc/fc_core.h"
#include "io/osd.h"
#include "fc/rc_controls.h"
#include "flight/pid.h"
#include "fc/settings.h"

int main() {
    printf("%zu\n", sizeof($STRUCT_TYPE));
    return 0;
}
EOF

# Compile and run
gcc -I src/main -I src/main/target/SITL -I src/main/common -I src/main/drivers \
    -I src/main/config -I . \
    /tmp/sizeof_test.c -o /tmp/sizeof_test 2>/dev/null && \
    /tmp/sizeof_test 2>/dev/null || echo "0"

rm -f /tmp/sizeof_test.c /tmp/sizeof_test
