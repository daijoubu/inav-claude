# Project: Analyze Pitch/Throttle/Airspeed Relationships from Flight Logs

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Data Analysis / Testing
**Created:** 2026-01-16
**Estimated Effort:** 8-12 hours

## Overview

Analyze real flight log data to understand how pitch and throttle affect airspeed. Design and implement scripts to find stable flight periods and match comparable segments with different control inputs, enabling empirical analysis of aircraft performance characteristics.

## Collaboration

**This is a collaborative task between Developer and Test Engineer:**
- **Developer:** Script design, implementation, data processing
- **Test Engineer:** Log analysis, test methodology, validation

The developer should coordinate with the test engineer throughout this project.

## Objectives

1. **Parse flight log data** from blackbox logs at `/home/raymorris/Downloads/LOG0005*`
2. **Identify stable periods** - segments with minimal change in airspeed, pitch, or throttle (2+ seconds)
3. **Match comparable periods** - find segments with similar conditions but different variables
4. **Analyze relationships** - determine how pitch and throttle affect airspeed from real data

## Data Sources

**Log Files:** `/home/raymorris/Downloads/LOG0005*`

**Key Data Fields:**
- **Airspeed** - Measured airspeed (cm/s or similar)
- **Pitch** - Aircraft pitch angle (degrees)
- **Throttle** - Motor throttle percentage or PWM value

**Additional Context Fields (if available):**
- Timestamp
- Altitude
- Motor outputs
- GPS groundspeed
- Wind conditions

## Phase 1: Stable Period Detection

### Goal
Find flight segments where airspeed, pitch, and throttle remain relatively constant for at least 2 seconds.

### Approach
1. **Define "stable":**
   - What is acceptable variance for each parameter?
   - Airspeed: ±X cm/s?
   - Pitch: ±Y degrees?
   - Throttle: ±Z%?

2. **Sliding window analysis:**
   - Use 2-second (or configurable) window
   - Calculate variance or standard deviation
   - Flag periods below threshold as "stable"

3. **Output format:**
   - Start time, end time, duration
   - Average values (airspeed, pitch, throttle)
   - Variance/std dev for each parameter
   - Additional context (altitude, etc.)

## Phase 2: Period Matching

### Goal
Find pairs or groups of stable periods that can be compared to isolate variable effects.

### Matching Scenarios

**Scenario A: Same throttle, different pitch/airspeed**
- Throttle within ±X%
- Different pitch angles
- Compare resulting airspeed differences
- **Analysis:** How does pitch affect airspeed at constant throttle?

**Scenario B: Same airspeed, different pitch/throttle**
- Airspeed within ±X cm/s
- Different pitch angles
- Different throttle values
- **Analysis:** How do pitch and throttle trade off to maintain airspeed?

**Scenario C: Same pitch, different throttle/airspeed**
- Pitch within ±X degrees
- Different throttle values
- Compare resulting airspeed
- **Analysis:** How does throttle affect airspeed at constant pitch?

### Matching Criteria
- Define acceptable tolerances for "same" values
- Consider altitude differences (air density)
- Account for wind conditions (if logged)
- Weight/battery voltage changes over flight

## Phase 3: Analysis and Visualization

### Data Analysis
- Statistical comparison of matched periods
- Calculate sensitivity coefficients (e.g., Δairspeed/Δthrottle)
- Identify trends and relationships
- Detect outliers or anomalies

### Visualization (Optional)
- Scatter plots: throttle vs airspeed (colored by pitch)
- Time series: show matched periods side-by-side
- 3D surface plot: pitch/throttle/airspeed relationship
- Heatmaps: sensitivity analysis

## Technical Approach

### Tools and Libraries
- **Python** recommended for data analysis
- **blackbox-tools** or similar for log parsing
- **pandas** for data manipulation
- **numpy** for numerical analysis
- **matplotlib/seaborn** for visualization (optional)

### Script Design

**Script 1: `find_stable_periods.py`**
```python
# Input: Flight log file(s)
# Output: CSV of stable periods with avg values and statistics
# Parameters: window_size, variance_thresholds
```

**Script 2: `match_periods.py`**
```python
# Input: Stable periods CSV
# Output: Matched period pairs/groups
# Parameters: matching_tolerances, matching_scenarios
```

**Script 3: `analyze_relationships.py`**
```python
# Input: Matched periods
# Output: Statistical analysis and visualizations
# Parameters: analysis_type, output_format
```

### Workflow
1. Parse logs → extract airspeed, pitch, throttle time series
2. Find stable periods → generate candidates CSV
3. Match periods → identify comparable segments
4. Analyze → calculate relationships and trends
5. Report → summarize findings

## Expected Deliverables

1. **Scripts (in `claude/developer/scripts/testing/`):**
   - `find_stable_periods.py` - Stable period detection
   - `match_periods.py` - Period matching algorithm
   - `analyze_relationships.py` - Statistical analysis
   - `README.md` - Usage documentation

2. **Data Outputs:**
   - `stable_periods.csv` - All detected stable periods
   - `matched_periods.csv` - Comparable period groups
   - `analysis_results.txt` - Statistical findings

3. **Analysis Report:**
   - Methodology explanation
   - Key findings about pitch/throttle/airspeed relationships
   - Limitations and caveats
   - Recommendations for future analysis

4. **Test Plan (with Test Engineer):**
   - Validation methodology
   - Known edge cases
   - Recommended flight patterns for better data collection

## Success Criteria

- [ ] Scripts successfully parse flight logs
- [ ] Stable periods detected with configurable thresholds
- [ ] Period matching algorithm identifies valid comparisons
- [ ] Statistical analysis produces meaningful insights
- [ ] Scripts documented and reusable
- [ ] Test engineer validates methodology
- [ ] Findings documented in analysis report

## Important Considerations

### Data Quality
- **Wind effects:** Groundspeed ≠ airspeed in wind
- **Altitude changes:** Air density affects performance
- **Battery voltage:** Degrading battery affects power
- **Weight changes:** Fuel/battery consumption during flight
- **Measurement noise:** Filter or smooth data appropriately

### Analysis Limitations
- **Correlation ≠ causation:** Other factors may affect results
- **Limited scenarios:** Real flights may not cover all combinations
- **Environmental factors:** Temperature, pressure, humidity
- **Aircraft configuration:** Payload, CG position, etc.

### Collaboration Points
The developer should coordinate with the test engineer on:
- Defining "stable" thresholds
- Choosing matching tolerances
- Validating detected periods
- Interpreting results
- Planning future test flights for better data

## Resources

- **Log Files:** `/home/raymorris/Downloads/LOG0005*`
- **Blackbox Tools:** Available in `blackbox-tools/` repository
- **INAV Blackbox Docs:** Log format documentation
- **Test Engineer:** Coordinate via email system

## Background

Understanding how pitch and throttle affect airspeed is crucial for:
- **Fixed-wing auto-throttle tuning** - TECS (Total Energy Control System)
- **Cruise flight optimization** - Efficiency vs speed tradeoffs
- **Performance envelope mapping** - Aircraft capabilities
- **Flight model validation** - Compare real vs simulated behavior

Real flight data provides empirical validation that can:
- Verify theoretical models
- Identify unexpected behaviors
- Guide parameter tuning
- Improve navigation algorithms

## Notes

- This is a **data analysis** task, not firmware modification
- Results may inform future firmware improvements
- Scripts should be **reusable** for future log analysis
- Consider making this a general-purpose log analysis framework
- Test engineer may have additional analysis requirements

## Estimated Effort

- Log parsing and data extraction: 2-3 hours
- Stable period detection script: 2-3 hours
- Period matching algorithm: 2-3 hours
- Analysis and visualization: 2-3 hours
- Documentation and testing: 1-2 hours
- **Total: 8-12 hours**

## Future Extensions

- Automated test flight planning for comprehensive coverage
- Real-time analysis during flight
- Integration with SITL for model validation
- Machine learning for performance prediction
- Multi-aircraft comparison
