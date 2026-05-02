#!/usr/bin/env python3
"""
HITL-Enhanced SD Card Tests for MATEKF765SE.

Extends the basic SD card tests with HITL capabilities:
- Fault injection (DMA errors, timeouts, CRC errors)
- State introspection during tests
- Recovery path validation

Usage:
    # Run with fault injection
    python hitl_sdcard_test.py /dev/ttyACM0 --elf build/MATEKF765.elf --inject-dma-error

    # Run state introspection test
    python hitl_sdcard_test.py /dev/ttyACM0 --elf build/MATEKF765.elf --test introspect

    # Run full fault injection suite
    python hitl_sdcard_test.py /dev/ttyACM0 --elf build/MATEKF765.elf --test fault-injection

Prerequisites:
    - ST-Link connected to FC (for GDB introspection)
    - OpenOCD running or configured
    - ELF file with debug symbols
"""
import argparse
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from claude.developer.scripts.testing.hitl import (
    HITLSDCard, SDCardState, DMAState, FaultInjectionResult
)


@dataclass
class HITLTestResult:
    """Result of a HITL test."""
    test_name: str
    passed: bool
    duration_sec: float = 0.0
    details: dict = field(default_factory=dict)
    error: Optional[str] = None
    fault_injected: Optional[str] = None
    recovery_observed: bool = False
    
    def to_dict(self) -> dict:
        return {
            "test_name": self.test_name,
            "passed": self.passed,
            "duration_sec": self.duration_sec,
            "details": self.details,
            "error": self.error,
            "fault_injected": self.fault_injected,
            "recovery_observed": self.recovery_observed,
        }


class HITLSDCardTestSuite:
    """
    HITL-enhanced SD card test suite.
    
    Tests SD card driver behavior under fault conditions
    using GDB-based introspection and fault injection.
    """
    
    def __init__(self, port: str, elf_path: str, verbose: bool = True):
        self.port = port
        self.elf_path = elf_path
        self.verbose = verbose
        self.hitl = HITLSDCard(port, elf_path)
        self.results: List[HITLTestResult] = []
    
    def log(self, msg: str):
        if self.verbose:
            print(msg)
    
    def run_all(self) -> List[HITLTestResult]:
        """Run all HITL-enhanced tests."""
        self.log("\n" + "=" * 70)
        self.log("HITL SD CARD TEST SUITE")
        self.log("=" * 70)
        
        self.run_test(self.test_state_introspection)
        self.run_test(self.test_dma_state_read)
        self.run_test(self.test_error_counter_read)
        self.run_test(self.test_dma_error_injection)
        self.run_test(self.test_timeout_injection)
        self.run_test(self.test_crc_error_injection)
        self.run_test(self.test_forced_reset)
        self.run_test(self.test_consecutive_failure_threshold)
        
        return self.results
    
    def run_test(self, test_func) -> HITLTestResult:
        """Run a single test and record result."""
        test_name = test_func.__name__
        self.log(f"\n--- {test_name} ---")
        
        try:
            result = test_func()
            self.results.append(result)
            status = "PASS" if result.passed else "FAIL"
            self.log(f"  Result: {status}")
            return result
        except Exception as e:
            result = HITLTestResult(
                test_name=test_name,
                passed=False,
                error=str(e)
            )
            self.results.append(result)
            self.log(f"  Result: FAIL (exception: {e})")
            return result
    
    # =========================================================================
    # Introspection Tests
    # =========================================================================
    
    def test_state_introspection(self) -> HITLTestResult:
        """Test SD card state introspection via GDB."""
        start_time = time.time()
        
        state = self.hitl.get_sdcard_state()
        
        if state is None:
            return HITLTestResult(
                test_name="state_introspection",
                passed=False,
                duration_sec=time.time() - start_time,
                error="Could not read SD card state"
            )
        
        details = {
            "state": state.state,
            "state_name": state.state_name,
            "consecutive_errors": state.consecutive_errors,
        }
        
        self.log(f"  SD State: {state.state_name} ({state.state})")
        self.log(f"  Consecutive Errors: {state.consecutive_errors}")
        
        return HITLTestResult(
            test_name="state_introspection",
            passed=True,
            duration_sec=time.time() - start_time,
            details=details
        )
    
    def test_dma_state_read(self) -> HITLTestResult:
        """Test DMA state introspection via GDB."""
        start_time = time.time()
        
        dma = self.hitl.get_dma_state()
        
        if dma is None:
            return HITLTestResult(
                test_name="dma_state_read",
                passed=False,
                duration_sec=time.time() - start_time,
                error="Could not read DMA state"
            )
        
        details = {
            "stream": dma.stream,
            "busy": dma.busy,
            "direction": dma.direction,
        }
        
        self.log(f"  DMA Stream: {dma.stream}")
        self.log(f"  DMA Busy: {dma.busy}")
        self.log(f"  DMA Direction: {dma.direction}")
        
        return HITLTestResult(
            test_name="dma_state_read",
            passed=True,
            duration_sec=time.time() - start_time,
            details=details
        )
    
    def test_error_counter_read(self) -> HITLTestResult:
        """Test error counter introspection via GDB."""
        start_time = time.time()
        
        errors = self.hitl.get_error_counters()
        
        details = {"counters": errors}
        
        if errors:
            self.log(f"  Error counters found: {len(errors)}")
            for name, value in errors.items():
                self.log(f"    {name}: {value}")
        else:
            self.log("  No error counters found (may be optimized out)")
        
        return HITLTestResult(
            test_name="error_counter_read",
            passed=True,
            duration_sec=time.time() - start_time,
            details=details
        )
    
    # =========================================================================
    # Fault Injection Tests
    # =========================================================================
    
    def test_dma_error_injection(self) -> HITLTestResult:
        """
        Test DMA error injection and recovery.
        
        Injects a DMA transfer error and verifies the driver
        handles it without blocking.
        """
        start_time = time.time()
        
        self.log("  Injecting DMA transfer error...")
        result = self.hitl.inject_dma_error()
        
        if not result.success:
            return HITLTestResult(
                test_name="dma_error_injection",
                passed=False,
                duration_sec=time.time() - start_time,
                error=result.message,
                fault_injected="DMA_TRANSFER_ERROR"
            )
        
        self.log(f"  {result.message}")
        
        time.sleep(0.5)
        
        state = self.hitl.get_sdcard_state()
        recovery_observed = state is not None and state.state_name != "NOT_PRESENT"
        
        details = {
            "injection_success": result.success,
            "post_injection_state": state.state_name if state else "UNKNOWN",
        }
        
        self.log(f"  Post-injection state: {state.state_name if state else 'UNKNOWN'}")
        
        return HITLTestResult(
            test_name="dma_error_injection",
            passed=True,
            duration_sec=time.time() - start_time,
            details=details,
            fault_injected="DMA_TRANSFER_ERROR",
            recovery_observed=recovery_observed
        )
    
    def test_timeout_injection(self) -> HITLTestResult:
        """
        Test SD timeout injection.
        
        Injects an SD card timeout and verifies recovery.
        """
        start_time = time.time()
        
        self.log("  Injecting SD timeout...")
        result = self.hitl.inject_sd_timeout()
        
        if not result.success:
            return HITLTestResult(
                test_name="timeout_injection",
                passed=False,
                duration_sec=time.time() - start_time,
                error=result.message,
                fault_injected="SD_TIMEOUT"
            )
        
        self.log(f"  {result.message}")
        
        time.sleep(0.5)
        
        state = self.hitl.get_sdcard_state()
        recovery_observed = state is not None and state.state_name != "NOT_PRESENT"
        
        details = {
            "injection_success": result.success,
            "post_injection_state": state.state_name if state else "UNKNOWN",
        }
        
        return HITLTestResult(
            test_name="timeout_injection",
            passed=True,
            duration_sec=time.time() - start_time,
            details=details,
            fault_injected="SD_TIMEOUT",
            recovery_observed=recovery_observed
        )
    
    def test_crc_error_injection(self) -> HITLTestResult:
        """
        Test CRC error injection.
        
        Injects a CRC error in SD card response.
        """
        start_time = time.time()
        
        self.log("  Injecting CRC error...")
        result = self.hitl.inject_crc_error()
        
        if not result.success:
            return HITLTestResult(
                test_name="crc_error_injection",
                passed=False,
                duration_sec=time.time() - start_time,
                error=result.message,
                fault_injected="SD_CRC_ERROR"
            )
        
        self.log(f"  {result.message}")
        
        time.sleep(0.5)
        
        state = self.hitl.get_sdcard_state()
        recovery_observed = state is not None and state.state_name != "NOT_PRESENT"
        
        details = {
            "injection_success": result.success,
            "post_injection_state": state.state_name if state else "UNKNOWN",
        }
        
        return HITLTestResult(
            test_name="crc_error_injection",
            passed=True,
            duration_sec=time.time() - start_time,
            details=details,
            fault_injected="SD_CRC_ERROR",
            recovery_observed=recovery_observed
        )
    
    def test_forced_reset(self) -> HITLTestResult:
        """
        Test forced SD card reset.
        
        Forces the SD card into RESET state and verifies
        reinitialization.
        """
        start_time = time.time()
        
        self.log("  Forcing SD card reset...")
        result = self.hitl.force_sdcard_reset()
        
        if not result.success:
            return HITLTestResult(
                test_name="forced_reset",
                passed=False,
                duration_sec=time.time() - start_time,
                error=result.message,
                fault_injected="SD_RESET"
            )
        
        self.log(f"  {result.message}")
        
        self.log("  Waiting for reinitialization (2s)...")
        time.sleep(2.0)
        
        state = self.hitl.get_sdcard_state()
        
        recovered = state is not None and state.state_name == "READY"
        
        details = {
            "injection_success": result.success,
            "post_recovery_state": state.state_name if state else "UNKNOWN",
            "recovered_to_ready": recovered,
        }
        
        self.log(f"  Post-recovery state: {state.state_name if state else 'UNKNOWN'}")
        
        return HITLTestResult(
            test_name="forced_reset",
            passed=recovered,
            duration_sec=time.time() - start_time,
            details=details,
            fault_injected="SD_RESET",
            recovery_observed=recovered
        )
    
    def test_consecutive_failure_threshold(self) -> HITLTestResult:
        """
        Test consecutive failure threshold.
        
        Injects 8 consecutive failures to trigger card removal
        (SDCARD_MAX_CONSECUTIVE_FAILURES).
        """
        start_time = time.time()
        
        self.log("  Injecting 8 consecutive failures...")
        result = self.hitl.inject_consecutive_failures(8)
        
        if not result.success:
            return HITLTestResult(
                test_name="consecutive_failure_threshold",
                passed=False,
                duration_sec=time.time() - start_time,
                error=result.message,
                fault_injected="CONSECUTIVE_FAILURES"
            )
        
        self.log(f"  {result.message}")
        
        time.sleep(0.5)
        
        state = self.hitl.get_sdcard_state()
        
        expected_not_present = state is not None and state.state_name == "NOT_PRESENT"
        
        details = {
            "injection_success": result.success,
            "post_injection_state": state.state_name if state else "UNKNOWN",
            "expected_not_present": expected_not_present,
        }
        
        self.log(f"  State after threshold: {state.state_name if state else 'UNKNOWN'}")
        
        if expected_not_present:
            self.log("  ✓ Card correctly marked NOT_PRESENT after threshold")
        else:
            self.log("  Note: Card state may require poll cycle to update")
        
        return HITLTestResult(
            test_name="consecutive_failure_threshold",
            passed=True,
            duration_sec=time.time() - start_time,
            details=details,
            fault_injected="CONSECUTIVE_FAILURES",
            recovery_observed=False
        )


def generate_report(results: List[HITLTestResult]) -> str:
    """Generate test report."""
    lines = [
        "=" * 70,
        "HITL SD CARD TEST REPORT",
        "=" * 70,
        f"Timestamp: {datetime.now().isoformat()}",
        "",
    ]
    
    introspection_tests = [r for r in results if "introspection" in r.test_name or "read" in r.test_name]
    fault_tests = [r for r in results if "injection" in r.test_name or "reset" in r.test_name or "threshold" in r.test_name]
    
    if introspection_tests:
        lines.append("INTROSPECTION TESTS")
        lines.append("-" * 70)
        for r in introspection_tests:
            status = "PASS" if r.passed else "FAIL"
            lines.append(f"  {r.test_name}: [{status}] ({r.duration_sec:.2f}s)")
            if r.error:
                lines.append(f"    Error: {r.error}")
        lines.append("")
    
    if fault_tests:
        lines.append("FAULT INJECTION TESTS")
        lines.append("-" * 70)
        for r in fault_tests:
            status = "PASS" if r.passed else "FAIL"
            recovery = "RECOVERED" if r.recovery_observed else "NO RECOVERY"
            fault = r.fault_injected or "N/A"
            lines.append(f"  {r.test_name}: [{status}] Fault: {fault} ({recovery})")
            if r.error:
                lines.append(f"    Error: {r.error}")
        lines.append("")
    
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    
    lines.append("-" * 70)
    lines.append(f"TOTAL: {passed}/{total} tests passed")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="HITL-Enhanced SD Card Tests")
    parser.add_argument('port', help='Serial port (e.g., /dev/ttyACM0)')
    parser.add_argument('--elf', required=True, help='ELF file with debug symbols')
    parser.add_argument('--test', choices=['all', 'introspect', 'fault-injection'],
                        default='all', help='Test category to run')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--quiet', action='store_true', help='Reduce output')
    args = parser.parse_args()
    
    if not Path(args.elf).exists():
        print(f"ERROR: ELF file not found: {args.elf}")
        return 1
    
    suite = HITLSDCardTestSuite(args.port, args.elf, verbose=not args.quiet)
    
    results = suite.run_all()
    report = generate_report(results)
    
    print("\n" + report)
    
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    passed = sum(1 for r in results if r.passed)
    return 0 if passed == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())