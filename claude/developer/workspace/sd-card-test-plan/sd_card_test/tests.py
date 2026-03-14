"""
SD Card Test Implementations.

Refactored tests using context managers and base classes.
"""
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

from .models import TestResult, SDCardStatus
from .test_base import TestBase, ArmedTest
from .contexts import FCContexts


class Test1Detection(TestBase):
    """Test 1: SD Card Detection & Initialization"""
    
    test_num = 1
    test_name = "SD Card Detection"
    
    def run(self, timeout_sec: float = 3.0) -> TestResult:
        self.log_header()
        self.log("  WARNING: MSP_SDCARD_SUMMARY can lock up FC if SD is in bad state")
        
        start = time.time()
        
        try:
            sd = self.fc.get_sd_card_status()
        except Exception as e:
            return self.error_result(f"Exception: {e}", time.time() - start)
        
        if not sd:
            return self.error_result("Failed to query SD card status", time.time() - start)
        
        details = {
            "supported": sd.supported,
            "state": sd.state_name,
            "fs_error": sd.fs_error,
            "free_space_mb": sd.free_space_kb / 1024,
            "total_space_mb": sd.total_space_kb / 1024,
        }
        
        self.log(f"  Supported: {sd.supported}")
        self.log(f"  State: {sd.state_name}")
        self.log(f"  FS Error: {sd.fs_error}")
        self.log(f"  Free Space: {details['free_space_mb']:.1f} MB")
        
        passed = sd.supported and sd.is_ready and sd.fs_error == 0 and sd.total_space_kb > 0
        self.log(f"  RESULT: {'PASS' if passed else 'FAIL'}")
        
        return TestResult(
            test_num=self.test_num,
            test_name=self.test_name,
            passed=passed,
            duration_sec=time.time() - start,
            details=details
        )


class Test2WriteSpeed(ArmedTest):
    """Test 2: Write Speed Measurement"""
    
    test_num = 2
    test_name = "Write Speed Measurement"
    
    def run(self, duration_sec: int = 60) -> TestResult:
        self.log_header()
        start = time.time()
        
        sd_before = self.validate_sd_ready()
        if not sd_before:
            return self.error_result("SD card not ready", time.time() - start)
        
        with self.contexts.armed(timeout=300) as armed:
            if not armed:
                return self.error_result(armed.error or "Failed to arm", time.time() - start)
            
            self.log(f"  Logging for {duration_sec} seconds...")
            self.fc.run_rc_loop(duration_sec)
        
        time.sleep(2)  # Flush
        sd_after = self.fc.get_sd_card_status()
        
        if not sd_after:
            return self.error_result("Failed to query SD after logging", time.time() - start)
        
        details = self.calculate_write_speed(sd_before, sd_after, duration_sec)
        details["duration_sec"] = duration_sec
        
        self.log(f"  KB written: {details['kb_written']}")
        self.log(f"  Write speed: {details['write_speed_kbps']:.1f} KB/s")
        
        passed = sd_after.is_ready and details["write_speed_kbps"] > 100
        self.log(f"  RESULT: {'PASS' if passed else 'FAIL'}")
        
        return TestResult(
            test_num=self.test_num,
            test_name=self.test_name,
            passed=passed,
            duration_sec=time.time() - start,
            details=details
        )


class Test3ContinuousLogging(ArmedTest):
    """Test 3: Continuous Logging with Servo Stress"""
    
    test_num = 3
    test_name = "Continuous Logging"
    
    def run(self, duration_min: int = 5) -> TestResult:
        self.log_header()
        duration_sec = duration_min * 60
        start = time.time()
        
        self.log(f"  Note: Running {duration_min} min test")
        
        sd_before = self.validate_sd_ready()
        if not sd_before:
            return self.error_result("SD card not ready", time.time() - start)
        
        errors = 0
        checks = 0
        
        with self.contexts.armed(timeout=300) as armed:
            if not armed:
                return self.error_result(armed.error or "Failed to arm", time.time() - start)
            
            # Start servo stress in background
            stress = self.fc.start_servo_stress_background(duration_sec, pattern='sweep')
            
            # Monitor SD card
            check_interval = duration_sec / 2
            while time.time() - start < duration_sec:
                time.sleep(check_interval)
                sd = self.fc.get_sd_card_status()
                checks += 1
                if not sd or not sd.is_ready:
                    errors += 1
                    self.log(f"  [{checks}] ERROR - SD not ready")
                else:
                    self.log(f"  [{checks}] OK - State: {sd.state_name}")
        
        self.fc.wait_for_servo_stress(stress)
        
        details = {
            "duration_min": duration_min,
            "checks_performed": checks,
            "errors_detected": errors,
        }
        
        passed = errors == 0
        self.log(f"  RESULT: {'PASS' if passed else 'FAIL'} ({errors} errors)")
        
        return TestResult(
            test_num=self.test_num,
            test_name=self.test_name,
            passed=passed,
            duration_sec=time.time() - start,
            details=details
        )


class Test4HighFrequency(Test2WriteSpeed):
    """Test 4: High-Frequency Logging (same as Test 2)"""
    
    test_num = 4
    test_name = "High-Frequency Logging"


class Test6ArmDisarmCycles(TestBase):
    """Test 6: Rapid Arm/Disarm Cycles"""
    
    test_num = 6
    test_name = "Arm/Disarm Cycles"
    
    def run(self, cycles: int = 20) -> TestResult:
        self.log_header()
        start = time.time()
        
        successful = 0
        
        for i in range(cycles):
            self.log(f"  Cycle {i+1}/{cycles}...")
            
            with self.contexts.armed(timeout=30) as armed:
                if not armed:
                    self.log(f"    Failed to arm: {armed.error}")
                    continue
                
                # Run short servo stress
                stress = self.fc.start_servo_stress_background(2.0, pattern='sweep')
                self.fc.wait_for_servo_stress(stress)
                successful += 1
                self.log(f"    ✓ Cycle {i+1} complete")
        
        details = {
            "target_cycles": cycles,
            "successful_cycles": successful,
        }
        
        passed = successful == cycles
        self.log(f"  RESULT: {'PASS' if passed else 'FAIL'} ({successful}/{cycles})")
        
        return TestResult(
            test_num=self.test_num,
            test_name=self.test_name,
            passed=passed,
            duration_sec=time.time() - start,
            details=details
        )


class Test7MSCLogVerification(TestBase):
    """Test 7: MSC Mode Log Download and Verification"""
    
    test_num = 7
    test_name = "MSC Log Verification"
    
    def run(self, max_logs: int = 2) -> TestResult:
        from .log_handler import LogHandler
        
        self.log_header()
        start = time.time()
        
        if not self.msc:
            return self.error_result("MSCHandler not provided", time.time() - start)
        
        log_handler = LogHandler(self.msc)
        
        # Step 1: Enter MSC mode
        self.log("  [1/4] Entering MSC mode...")
        if not self.msc.enable_msc_mode(timeout=30.0):
            return self.error_result("Failed to enter MSC mode", time.time() - start)
        self.log("  ✓ MSC mode enabled")
        
        # Step 2: Download logs
        self.log("  [2/4] Downloading logs...")
        logs = log_handler.download_logs_from_msc(max_logs=max_logs)
        if not logs:
            return self.error_result("No logs downloaded", time.time() - start)
        self.log(f"  ✓ Downloaded {len(logs)} logs")
        
        # Step 3: Verify logs
        self.log("  [3/4] Verifying logs...")
        verified = 0
        total_frames = 0
        for path, data in logs:
            result = log_handler.verify_blackbox_log(data)
            if result.passed:
                verified += 1
                total_frames += result.frame_count
            self.log(f"    {path.name}: {'PASS' if result.passed else 'FAIL'} ({result.frame_count} frames)")
        
        # Step 4: Exit MSC mode
        self.log("  [4/4] Exiting MSC mode...")
        if not self.msc.exit_msc_mode(openocd_config="openocd_matekf765_no_halt.cfg"):
            self.log("  ⚠ Exit returned False (may still work)")
        else:
            self.log("  ✓ MSC mode exited")
        
        # Wait for CDC
        import os
        time.sleep(2)
        cdc_restored = os.path.exists('/dev/ttyACM0')
        
        details = {
            "logs_downloaded": len(logs),
            "logs_verified": verified,
            "total_frames": total_frames,
            "cdc_restored": cdc_restored,
        }
        
        passed = verified == len(logs) and cdc_restored
        self.log(f"  RESULT: {'PASS' if passed else 'FAIL'}")
        
        return TestResult(
            test_num=self.test_num,
            test_name=self.test_name,
            passed=passed,
            duration_sec=time.time() - start,
            details=details
        )


class Test8GPSArm(ArmedTest):
    """Test 8: GPS Fix + Immediate Arm (F765 lockup specific)"""
    
    test_num = 8
    test_name = "GPS Fix + Immediate Arm"
    
    def run(self, attempts: int = 10, gps_timeout: float = 300) -> TestResult:
        self.log_header()
        self.log("  This test reproduces the F765 arming lockup scenario.")
        self.log("  Requires GPS module connected and receiving signal.")
        
        start = time.time()
        details = {"target_attempts": attempts}
        successful_arms = 0
        lockups_detected = 0
        
        for i in range(attempts):
            self.log(f"\n  Attempt {i+1}/{attempts}:")
            
            gps = self.fc.get_gps_status()
            if not gps:
                self.log("    ERROR: Cannot query GPS status")
                continue
            
            self.log(f"    GPS: {gps.fix_name}, {gps.num_sat} sats")
            
            if not gps.has_fix:
                self.log(f"    Waiting for GPS fix (timeout: {gps_timeout}s)...")
                if not self.fc.wait_for_gps_fix(timeout=gps_timeout):
                    self.log("    WARNING: GPS fix timeout")
                    continue
                self.log("    GPS fix acquired!")
            
            self.log(f"    Checking arming status...")
            ready, status_msg = self.fc.wait_for_arming_ready(timeout=10.0)
            if not ready:
                self.log(f"    WARNING: Not ready to arm: {status_msg}")
                continue
            
            arm_time = time.time()
            arm_result = self.fc.arm(timeout=2.0)
            response_time = time.time() - arm_time
            
            if not arm_result:
                self.log(f"    WARNING: Arm command timed out after {response_time*1000:.1f}ms")
                
                arming = self.fc.get_arming_status()
                if arming is None:
                    lockups_detected += 1
                    self.log(f"    LOCKUP DETECTED! FC not responding after arm attempt")
                    
                    self.log("    Waiting 5s for recovery...")
                    time.sleep(5)
                    recovery = self.fc.get_arming_status()
                    if recovery:
                        self.log("    FC recovered")
                    else:
                        self.log("    FC still unresponsive - may need power cycle")
            else:
                successful_arms += 1
                self.log(f"    ✓ Armed successfully in {response_time*1000:.1f}ms")
                
                self.log(f"    Servo stress for 2 seconds...")
                self.fc.move_servos(duration=2.0, pattern='random', rate_hz=15.0)
                
                self.fc.disarm(timeout=2.0)
                self.log(f"    Disarmed")
            
            time.sleep(2)
        
        details["successful_arms"] = successful_arms
        details["lockups_detected"] = lockups_detected
        
        passed = successful_arms == attempts and lockups_detected == 0
        
        self.log(f"\n  RESULT: {'PASS' if passed else 'FAIL'}")
        self.log(f"  Successful: {successful_arms}/{attempts}, Lockups: {lockups_detected}")
        
        return TestResult(
            test_num=self.test_num,
            test_name=self.test_name,
            passed=passed,
            duration_sec=time.time() - start,
            details=details
        )


class Test9ExtendedEndurance(ArmedTest):
    """Test 9: Extended Endurance Test (long-duration stability)"""
    
    test_num = 9
    test_name = "Extended Endurance"
    
    def run(self, duration_min: int = 60) -> TestResult:
        self.log_header()
        self.log("  Continuous logging with periodic arm/disarm cycles.")
        self.log("  Monitors SD card stability and performance over time.")
        
        start = time.time()
        duration_sec = duration_min * 60
        details = {"duration_min": duration_min}
        
        arm_cycles = 0
        disarm_cycles = 0
        sd_errors = 0
        msp_timeouts = 0
        write_speeds = []
        free_space_samples = []
        last_free_space = None
        
        initial_sd = self.fc.get_sd_card_status()
        if initial_sd:
            last_free_space = initial_sd.free_space_kb
            details["initial_free_space_mb"] = initial_sd.free_space_kb / 1024
        else:
            self.log("  WARNING: Cannot query initial SD card status")
            return self.error_result("Cannot query SD card status", time.time() - start)
        
        self.log(f"  Initial free space: {last_free_space/1024:.1f} MB")
        
        ready, status_msg = self.fc.wait_for_arming_ready(timeout=300.0)
        if not ready:
            self.log(f"  WARNING: FC not ready for arming: {status_msg}")
        else:
            self.log(f"  ✓ FC ready for arming")
        
        self.log(f"  Running for {duration_min} minutes...")
        
        typical_write_speed_kbps = 70
        estimated_data_mb = (typical_write_speed_kbps * duration_min * 60) / 1024 / 1024
        estimated_final_free_mb = (last_free_space / 1024) - estimated_data_mb
        min_safe_free_mb = 100
        
        if estimated_final_free_mb < min_safe_free_mb:
            self.log(f"  ⚠ WARNING: Test may run out of space!")
        
        check_interval = 10
        arm_interval = 30
        last_arm_attempt = time.time()
        min_free_mb = 100
        sd_status = None
        
        while time.time() - start < duration_sec:
            elapsed = time.time() - start
            elapsed_min = elapsed / 60
            
            if time.time() - last_arm_attempt >= arm_interval:
                last_arm_attempt = time.time()
                
                try:
                    if self.fc.arm(timeout=2.0):
                        arm_cycles += 1
                        self.fc.move_servos(duration=1.0, pattern='sweep', rate_hz=12.0)
                        time.sleep(1)
                        if self.fc.disarm(timeout=2.0):
                            disarm_cycles += 1
                except Exception:
                    pass
            
            try:
                sd_status = self.fc.get_sd_card_status()
                
                if sd_status:
                    free_space_samples.append((elapsed, sd_status.free_space_kb))
                    current_free_space = sd_status.free_space_kb
                    current_free_mb = current_free_space / 1024
                    
                    if last_free_space is not None and last_free_space > current_free_space:
                        bytes_written = (last_free_space - current_free_space) * 1024
                        write_speed_kbps = bytes_written / 1024 / check_interval
                        write_speeds.append(write_speed_kbps)
                    
                    last_free_space = current_free_space
                    
                    if not sd_status.is_ready:
                        sd_errors += 1
                        self.log(f"  [{elapsed_min:.1f}m] ⚠ SD Error: {sd_status.state_name}")
                    
                    if current_free_mb < min_free_mb:
                        self.log(f"  [{elapsed_min:.1f}m] ⚠ STOPPING: Free space critical ({current_free_mb:.1f} MB)")
                        break
                else:
                    msp_timeouts += 1
            except Exception:
                msp_timeouts += 1
            
            if int(elapsed) % 30 == 0:
                if sd_status:
                    free_mb = sd_status.free_space_kb / 1024
                    if write_speeds:
                        avg_speed = sum(write_speeds[-3:]) / len(write_speeds[-3:])
                        self.log(f"  [{elapsed_min:.1f}m] Free: {free_mb:.1f}MB, Cycles: {arm_cycles}/{disarm_cycles}, Write: {avg_speed:.1f} KB/s")
                    else:
                        self.log(f"  [{elapsed_min:.1f}m] Free: {free_mb:.1f}MB, Cycles: {arm_cycles}/{disarm_cycles}")
            
            time.sleep(check_interval)
        
        details["arm_cycles"] = arm_cycles
        details["disarm_cycles"] = disarm_cycles
        details["sd_errors"] = sd_errors
        details["msp_timeouts"] = msp_timeouts
        
        if write_speeds:
            details["avg_write_speed_kbps"] = sum(write_speeds) / len(write_speeds)
            details["min_write_speed_kbps"] = min(write_speeds)
            details["max_write_speed_kbps"] = max(write_speeds)
        else:
            details["avg_write_speed_kbps"] = 0
        
        if free_space_samples:
            initial_free = free_space_samples[0][1]
            final_free = free_space_samples[-1][1]
            details["total_written_mb"] = (initial_free - final_free) / 1024
        else:
            details["total_written_mb"] = 0
        
        passed = sd_errors == 0 and msp_timeouts < 5
        
        self.log(f"\n  RESULT: {'PASS' if passed else 'FAIL'}")
        self.log(f"  Arm/Disarm cycles: {arm_cycles}")
        self.log(f"  SD errors: {sd_errors}")
        self.log(f"  MSP timeouts: {msp_timeouts}")
        if details.get("avg_write_speed_kbps", 0) > 0:
            self.log(f"  Write speed: {details['avg_write_speed_kbps']:.1f} KB/s")
        if details.get("total_written_mb", 0) > 0:
            self.log(f"  Data written: {details['total_written_mb']:.1f} MB")
        
        return TestResult(
            test_num=self.test_num,
            test_name=self.test_name,
            passed=passed,
            duration_sec=time.time() - start,
            details=details
        )


class Test10DMAContention(ArmedTest):
    """Test 10: DMA Contention Stress Test (concurrent SD/GPS)"""
    
    test_num = 10
    test_name = "DMA Contention Stress"
    
    def run(self, duration_min: int = 10) -> TestResult:
        self.log_header()
        self.log("  Monitors SD card and GPS under simultaneous DMA load.")
        self.log("  Requires: GPS module connected with active fix.")
        
        start = time.time()
        duration_sec = duration_min * 60
        details = {"duration_min": duration_min}
        
        sd_errors = 0
        gps_dropouts = 0
        msp_timeouts = 0
        checks = 0
        
        check_interval = 5
        
        gps = self.fc.get_gps_status()
        if not gps or not gps.has_fix:
            self.log("  WARNING: GPS does not have fix. Test may be less meaningful.")
            details["gps_fix_at_start"] = False
        else:
            self.log(f"  GPS: {gps.num_sat} satellites, HDOP {gps.hdop}")
            details["gps_fix_at_start"] = True
            details["initial_satellites"] = gps.num_sat
        
        self.log(f"  Running for {duration_min} minutes...")
        self.log(f"  Starting servo stress (sweep pattern) for DMA contention...")
        
        servo_stress = self.fc.start_servo_stress_background(duration_sec, pattern='sweep', rate_hz=15.0)
        
        prev_gps_fix = gps.has_fix if gps else False
        
        while time.time() - start < duration_sec:
            checks += 1
            
            query_start = time.time()
            sd_status = self.fc.get_sd_card_status()
            gps_status = self.fc.get_gps_status()
            arming_status = self.fc.get_arming_status()
            query_time = (time.time() - query_start) * 1000
            
            issues = []
            
            if sd_status is None:
                msp_timeouts += 1
                issues.append("MSP timeout (SD)")
            elif not sd_status.is_ready:
                sd_errors += 1
                issues.append(f"SD error: {sd_status.state_name}")
            
            if gps_status is None:
                msp_timeouts += 1
                issues.append("MSP timeout (GPS)")
            elif prev_gps_fix and not gps_status.has_fix:
                gps_dropouts += 1
                issues.append("GPS fix lost")
            
            if arming_status is None:
                msp_timeouts += 1
                issues.append("MSP timeout (STATUS)")
            
            elapsed = time.time() - start
            if checks % 6 == 0 or issues:
                status_str = ", ".join(issues) if issues else "OK"
                sat_str = f"{gps_status.num_sat}sat" if gps_status else "?"
                sd_str = sd_status.state_name if sd_status else "?"
                self.log(f"  [{elapsed/60:.1f}m] {status_str} | GPS:{sat_str} SD:{sd_str} MSP:{query_time:.0f}ms")
            
            if gps_status:
                prev_gps_fix = gps_status.has_fix
            
            time.sleep(check_interval)
        
        self.fc.wait_for_servo_stress(servo_stress)
        
        details["checks_performed"] = checks
        details["sd_errors"] = sd_errors
        details["gps_dropouts"] = gps_dropouts
        details["msp_timeouts"] = msp_timeouts
        details["total_issues"] = sd_errors + gps_dropouts + msp_timeouts
        
        passed = sd_errors == 0 and gps_dropouts == 0 and msp_timeouts == 0
        
        self.log(f"\n  RESULT: {'PASS' if passed else 'FAIL'}")
        self.log(f"  SD errors: {sd_errors}, GPS dropouts: {gps_dropouts}, MSP timeouts: {msp_timeouts}")
        
        return TestResult(
            test_num=self.test_num,
            test_name=self.test_name,
            passed=passed,
            duration_sec=time.time() - start,
            details=details
        )


class Test11BlockingMeasurement(TestBase):
    """Test 11: Blocking Measurement using ST-Link + GDB"""
    
    test_num = 11
    test_name = "Blocking Measurement"
    
    def run(self, elf_path: Optional[str] = None, duration_sec: int = 60) -> TestResult:
        import sys
        from pathlib import Path
        
        self.log_header()
        
        start = time.time()
        
        if not elf_path:
            possible_paths = [
                Path("build/MATEKF765.elf"),
                Path("build_MATEKF765/MATEKF765.elf"),
                Path("../inav/build/MATEKF765.elf"),
            ]
            for p in possible_paths:
                if p.exists():
                    elf_path = str(p)
                    break
        
        if not elf_path:
            return self.error_result("ELF file not found. Specify with --elf parameter.", time.time() - start)
        
        self.log(f"  Using ELF: {elf_path}")
        self.log(f"  Duration: {duration_sec} seconds")
        self.log("  NOTE: This test requires ST-Link connected to the FC.")
        
        script_path = Path(__file__).parent.parent / "test_11_blocking.py"
        
        if not script_path.exists():
            return self.error_result(f"test_11_blocking.py not found at {script_path}", time.time() - start)
        
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(script_path), elf_path, "--duration", str(duration_sec)],
                capture_output=True,
                text=True,
                timeout=duration_sec + 60
            )
            
            self.log(result.stdout)
            if result.stderr:
                self.log(f"STDERR: {result.stderr}")
            
            max_blocking = 0.0
            for line in result.stdout.split('\n'):
                if "Maximum blocking time:" in line:
                    try:
                        max_blocking = float(line.split(':')[1].strip().replace('ms', ''))
                    except ValueError:
                        pass
            
            passed = result.returncode == 0
            details = {
                "max_blocking_ms": max_blocking,
                "elf_path": elf_path,
                "duration_sec": duration_sec
            }
            
            return TestResult(
                test_num=self.test_num,
                test_name=self.test_name,
                passed=passed,
                duration_sec=time.time() - start,
                details=details
            )
            
        except subprocess.TimeoutExpired:
            return self.error_result("Test timed out", time.time() - start)
        except Exception as e:
            return self.error_result(f"Exception: {e}", time.time() - start)


class TestSuite:
    """
    Test suite runner.
    
    Usage:
        suite = TestSuite(fc, msc)
        results = suite.run_all(tests=[1, 2, 3, 4, 6])
    """
    
    TEST_MAP = {
        1: Test1Detection,
        2: Test2WriteSpeed,
        3: Test3ContinuousLogging,
        4: Test4HighFrequency,
        6: Test6ArmDisarmCycles,
        7: Test7MSCLogVerification,
        8: Test8GPSArm,
        9: Test9ExtendedEndurance,
        10: Test10DMAContention,
        11: Test11BlockingMeasurement,
    }
    
    def __init__(self, fc, msc=None, verbose=True):
        self.fc = fc
        self.msc = msc
        self.verbose = verbose
        self.sd_card_info = {}
    
    def validate_sd_card(self, min_free_mb: float = 100.0) -> bool:
        """Validate SD card is ready with sufficient space."""
        sd = self.fc.get_sd_card_status()
        if not sd or not sd.is_ready:
            return False
        
        self.sd_card_info = {
            "state": sd.state_name,
            "free_space_mb": sd.free_space_kb / 1024,
            "total_space_mb": sd.total_space_kb / 1024,
        }
        
        return sd.free_space_kb / 1024 >= min_free_mb
    
    def run_test(self, test_num: int, **kwargs) -> TestResult:
        """Run a single test."""
        if test_num not in self.TEST_MAP:
            return TestResult(
                test_num=test_num,
                test_name="Unknown",
                passed=False,
                error=f"Test {test_num} not implemented"
            )
        
        test_cls = self.TEST_MAP[test_num]
        test = test_cls(self.fc, self.msc, self.verbose)
        return test.run(**kwargs)
    
    def run_all(self, tests: Optional[List[int]] = None, **kwargs) -> List[TestResult]:
        """Run all specified tests."""
        if tests is None:
            tests = [1, 2, 3, 4, 6]
        
        results = []
        for test_num in tests:
            result = self.run_test(test_num, **kwargs)
            results.append(result)
        
        return results
