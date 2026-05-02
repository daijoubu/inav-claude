# Proposed Refactored Structure

## File Organization

```
sd_card_test/
├── __init__.py
├── models.py           # Data classes (~100 lines)
├── msp.py              # MSP protocol constants & parsing (~150 lines)
├── connection.py       # Base MSP connection (~150 lines)
├── fc_control.py       # Arming, RC, GPS operations (~300 lines)
├── msc_handler.py      # USB Mass Storage operations (~400 lines)
├── cli_handler.py      # CLI command handling (~200 lines)
├── config_handler.py   # FC configuration validation/apply (~300 lines)
├── log_handler.py      # Log download & verification (~250 lines)
├── contexts.py         # Context managers (armed, msc) (~100 lines)
├── test_base.py        # Base test class with common patterns (~200 lines)
├── tests.py            # Test implementations (~600 lines)
└── main.py             # CLI entry point (~100 lines)
```

## Key Improvements

### 1. Context Managers for Repeated Patterns

Instead of:
```python
# Repeated in multiple tests
ready, msg = fc.wait_for_arming_ready()
if not ready:
    return TestResult(..., error=msg)
if not fc.arm():
    return TestResult(..., error="Failed to arm")
try:
    # ... test logic ...
finally:
    fc.disarm()
```

Use:
```python
with fc.armed_context() as ctx:
    if not ctx.success:
        return TestResult(..., error=ctx.error)
    # ... test logic ...
# Auto-disarms on exit
```

### 2. Split FCConnection into Focused Classes

**Current:** FCConnection (43 methods, ~1800 lines)
**Proposed:**
- `MSPConnection` - Low-level MSP protocol
- `FCControl` - Arming, RC, GPS (uses MSPConnection)
- `MSCHandler` - USB Mass Storage (standalone)
- `CLIHandler` - CLI commands (serial-based)
- `ConfigHandler` - Configuration management
- `LogHandler` - Log download/verification

### 3. Base Test Class

```python
class TestBase:
    """Common test patterns"""
    
    def __init__(self, fc: MSPConnection, verbose: bool = True):
        self.fc = fc
        self.verbose = verbose
    
    def log(self, msg: str):
        if self.verbose:
            print(msg)
    
    def run_armed_test(self, duration: float, test_func: Callable) -> TestResult:
        """Common pattern: arm, run test, disarm, return result"""
        with self.fc.armed_context() as ctx:
            if not ctx.success:
                return self._error_result(ctx.error)
            return test_func(duration)
    
    def _error_result(self, error: str) -> TestResult:
        return TestResult(test_num=self.test_num, ..., error=error)
```

### 4. Reduced Test Boilerplate

**Current test_2 (~150 lines):**
```python
def test_2_write_speed(self, duration_sec: int = 60) -> TestResult:
    self.log("="*60)
    self.log(f"TEST 2: Write Speed Measurement ({duration_sec}s)")
    # ... 40 lines of arming setup ...
    # ... 20 lines of RC loop ...
    # ... 30 lines of cleanup & calculation ...
```

**Refactored (~50 lines):**
```python
def test_2_write_speed(self, duration_sec: int = 60) -> TestResult:
    self.log_header(2, f"Write Speed Measurement ({duration_sec}s)")
    
    sd_before = self.fc.get_sd_card_status()
    
    with self.fc.armed_context(timeout=300) as ctx:
        if not ctx:
            return self.error_result(2, ctx.error)
        
        self.fc.run_rc_loop(duration_sec)  # Encapsulated
    
    sd_after = self.fc.get_sd_card_status()
    return self.calculate_write_speed(2, sd_before, sd_after, duration_sec)
```

## Benefits

1. **Maintainability** - Each file has single responsibility
2. **Testability** - Can unit test individual components
3. **Reusability** - MSPConnection can be used by other tools
4. **Readability** - ~200-400 lines per file vs 4000+ lines
5. **Extensibility** - Easy to add new tests or handlers

## Migration Plan

1. Extract models.py (no dependencies)
2. Extract msp.py constants
3. Create MSPConnection from FCConnection core
4. Create context managers
5. Create TestBase class
6. Migrate tests one by one
7. Update imports in main.py
