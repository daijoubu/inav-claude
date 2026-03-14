"""
GDB Python script for measuring blocking times in SD card operations.

This script sets breakpoints at critical SD card functions and measures
the time spent in each call. Used for Test 11 (Blocking Measurement).

Usage:
    gdb-multiarch -x gdb_timing.py <firmware.elf>

Or from GDB:
    source gdb_timing.py
    sd_timing_start
    # ... trigger SD operations ...
    sd_timing_report
"""

import gdb
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# =============================================================================
# Timing Data Structures
# =============================================================================

@dataclass
class TimingEntry:
    """Single timing measurement"""
    function: str
    file: str
    line: int
    start_time: float
    end_time: float = 0.0

    @property
    def duration_ms(self) -> float:
        if self.end_time > 0:
            return (self.end_time - self.start_time) * 1000
        return 0.0


@dataclass
class TimingStats:
    """Statistics for a breakpoint location"""
    function: str
    hit_count: int = 0
    total_time_ms: float = 0.0
    max_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    measurements: List[float] = field(default_factory=list)

    def add_measurement(self, duration_ms: float):
        self.hit_count += 1
        self.total_time_ms += duration_ms
        self.max_time_ms = max(self.max_time_ms, duration_ms)
        self.min_time_ms = min(self.min_time_ms, duration_ms)
        self.measurements.append(duration_ms)

    @property
    def avg_time_ms(self) -> float:
        return self.total_time_ms / self.hit_count if self.hit_count > 0 else 0.0


# =============================================================================
# Global State
# =============================================================================

class SDTimingMonitor:
    """Monitors SD card operation timing via GDB breakpoints"""

    # Critical functions to monitor (from F765 lockup investigation)
    BREAKPOINTS = [
        # HAL SD Init - main blocking call
        ("HAL_SD_Init", "stm32f7xx_hal_sd.c", None),
        ("HAL_SD_InitCard", "stm32f7xx_hal_sd.c", None),

        # SDIO driver reset - calls HAL_SD_Init
        ("SD_Init", "sdmmc_sdio_hal.c", None),
        ("sdcardSdio_reset", "sdcard_sdio.c", None),

        # Poll function - contains goto doMore loop
        ("sdcardSdio_poll", "sdcard_sdio.c", None),

        # Blackbox start - triggers SD operations at arm
        ("blackboxStart", "blackbox.c", None),
    ]

    def __init__(self):
        self.active = False
        self.stats: Dict[str, TimingStats] = {}
        self.current_entry: Optional[TimingEntry] = None
        self.breakpoints: List[gdb.Breakpoint] = []
        self.start_time = 0.0

    def start(self):
        """Start timing measurement"""
        print("SD Timing Monitor: Starting...")
        self.active = True
        self.stats.clear()
        self.start_time = time.time()
        self._setup_breakpoints()
        print(f"SD Timing Monitor: {len(self.breakpoints)} breakpoints set")

    def stop(self):
        """Stop timing measurement"""
        print("SD Timing Monitor: Stopping...")
        self.active = False
        self._clear_breakpoints()

    def _setup_breakpoints(self):
        """Set up breakpoints at critical functions"""
        self._clear_breakpoints()

        for func_name, file_hint, line in self.BREAKPOINTS:
            try:
                # Try to set breakpoint by function name
                bp = TimingBreakpoint(func_name, self)
                self.breakpoints.append(bp)
                self.stats[func_name] = TimingStats(function=func_name)
                print(f"  Breakpoint set: {func_name}")
            except gdb.error as e:
                print(f"  Warning: Could not set breakpoint at {func_name}: {e}")

    def _clear_breakpoints(self):
        """Remove all timing breakpoints"""
        for bp in self.breakpoints:
            bp.delete()
        self.breakpoints.clear()

    def record_entry(self, func_name: str, frame: gdb.Frame):
        """Record function entry"""
        if not self.active:
            return

        self.current_entry = TimingEntry(
            function=func_name,
            file=frame.find_sal().symtab.filename if frame.find_sal().symtab else "unknown",
            line=frame.find_sal().line,
            start_time=time.time()
        )

    def record_exit(self, func_name: str):
        """Record function exit and calculate duration"""
        if not self.active or not self.current_entry:
            return

        if self.current_entry.function == func_name:
            self.current_entry.end_time = time.time()
            duration = self.current_entry.duration_ms

            if func_name in self.stats:
                self.stats[func_name].add_measurement(duration)

            # Alert if blocking time exceeds threshold
            if duration > 10:  # > 10ms is concerning
                print(f"  *** BLOCKING: {func_name} took {duration:.1f}ms ***")

            self.current_entry = None

    def report(self):
        """Print timing report"""
        elapsed = time.time() - self.start_time

        print("\n" + "=" * 70)
        print("SD CARD TIMING REPORT")
        print("=" * 70)
        print(f"Monitoring duration: {elapsed:.1f}s")
        print("")

        # Sort by max time (most concerning first)
        sorted_stats = sorted(
            self.stats.values(),
            key=lambda s: s.max_time_ms,
            reverse=True
        )

        print(f"{'Function':<30} {'Hits':>6} {'Avg':>10} {'Max':>10} {'Total':>10}")
        print("-" * 70)

        for stat in sorted_stats:
            if stat.hit_count > 0:
                flag = " ***" if stat.max_time_ms > 10 else ""
                print(f"{stat.function:<30} {stat.hit_count:>6} "
                      f"{stat.avg_time_ms:>9.2f}ms {stat.max_time_ms:>9.2f}ms "
                      f"{stat.total_time_ms:>9.2f}ms{flag}")

        print("-" * 70)

        # Summary
        total_blocking = sum(s.total_time_ms for s in sorted_stats)
        max_single = max((s.max_time_ms for s in sorted_stats), default=0)

        print(f"Total time in monitored functions: {total_blocking:.2f}ms")
        print(f"Maximum single call duration: {max_single:.2f}ms")

        if max_single > 10:
            print("\n*** WARNING: Blocking calls detected (>10ms) ***")
            print("This may cause FC lockup during arming!")
        elif max_single > 5:
            print("\n* CAUTION: Some calls approaching blocking threshold (>5ms)")
        else:
            print("\nOK: No significant blocking detected")

        print("=" * 70)

        return {
            "duration_sec": elapsed,
            "total_blocking_ms": total_blocking,
            "max_single_ms": max_single,
            "stats": {name: {
                "hits": s.hit_count,
                "avg_ms": s.avg_time_ms,
                "max_ms": s.max_time_ms,
                "total_ms": s.total_time_ms
            } for name, s in self.stats.items() if s.hit_count > 0}
        }


class TimingBreakpoint(gdb.Breakpoint):
    """Breakpoint that records timing on entry"""

    def __init__(self, function: str, monitor: SDTimingMonitor):
        super().__init__(function)
        self.function = function
        self.monitor = monitor

    def stop(self):
        """Called when breakpoint is hit"""
        frame = gdb.selected_frame()
        self.monitor.record_entry(self.function, frame)

        # Set a finish breakpoint to measure exit time
        try:
            FinishBreakpoint(self.function, self.monitor)
        except gdb.error:
            pass  # Function may not have debug info for finish

        return False  # Don't stop execution


class FinishBreakpoint(gdb.FinishBreakpoint):
    """Temporary breakpoint to catch function return"""

    def __init__(self, function: str, monitor: SDTimingMonitor):
        super().__init__(internal=True)
        self.function = function
        self.monitor = monitor

    def stop(self):
        """Called when function returns"""
        self.monitor.record_exit(self.function)
        return False  # Don't stop execution

    def out_of_scope(self):
        """Called if breakpoint goes out of scope"""
        self.monitor.record_exit(self.function)


# =============================================================================
# Global Monitor Instance
# =============================================================================

_monitor = SDTimingMonitor()


# =============================================================================
# GDB Commands
# =============================================================================

class SDTimingStartCommand(gdb.Command):
    """Start SD card timing measurement"""

    def __init__(self):
        super().__init__("sd_timing_start", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        _monitor.start()
        print("Use 'sd_timing_report' to see results")
        print("Use 'sd_timing_stop' to stop monitoring")


class SDTimingStopCommand(gdb.Command):
    """Stop SD card timing measurement"""

    def __init__(self):
        super().__init__("sd_timing_stop", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        _monitor.stop()


class SDTimingReportCommand(gdb.Command):
    """Print SD card timing report"""

    def __init__(self):
        super().__init__("sd_timing_report", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        _monitor.report()


# Register commands
SDTimingStartCommand()
SDTimingStopCommand()
SDTimingReportCommand()

print("SD Timing Monitor loaded.")
print("Commands: sd_timing_start, sd_timing_stop, sd_timing_report")
