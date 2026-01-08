# Anomaly Detection Specification

## Overview

Specification for detecting system resource anomalies that trigger AI suggestions.

## Threshold Definitions

### CPU Anomaly
- **Trigger**: CPU usage > 80%
- **Duration**: Sustained for > 3 seconds
- **Metric**: Overall CPU percentage
- **Severity Levels**:
  - **Warning**: 80-90%
  - **Critical**: > 90%

### Memory Anomaly
- **Trigger**: Memory usage > 90%
- **Duration**: Sustained for > 5 seconds
- **Metric**: Memory percentage (used/total)
- **Severity Levels**:
  - **Warning**: 90-95%
  - **Critical**: > 95%

### Process Anomaly
- **Trigger**: Single process using > 50% of CPU or Memory
- **Duration**: Sustained for > 5 seconds
- **Metrics**:
  - Process CPU percentage
  - Process memory percentage
- **Severity Levels**:
  - **Warning**: 50-75%
  - **Critical**: > 75%

### Disk I/O Anomaly
- **Trigger**: Read or Write > 200 MB/s
- **Duration**: Sustained for > 10 seconds
- **Metric**: Disk I/O bytes per second
- **Severity**: Info only (not critical)

## Detection Algorithm

### State Machine
Each anomaly type maintains a state:
- **NORMAL**: No anomaly detected
- **POTENTIAL**: Threshold crossed but not sustained
- **CONFIRMED**: Threshold sustained for required duration
- **ACKNOWLEDGED**: User notified (AI suggestion shown)

### Transition Logic
```
NORMAL → POTENTIAL: Threshold crossed
POTENTIAL → CONFIRMED: Duration requirement met
CONFIRMED → ACKNOWLEDGED: AI suggestion triggered
ACKNOWLEDGED → NORMAL: Threshold drops below threshold
POTENTIAL → NORMAL: Threshold drops before duration met
```

### Cooldown Period
After transitioning to ACKNOWLEDGED:
- **Cooldown**: 60 seconds
- **Purpose**: Avoid spam for same issue
- **Reset**: Only after returning to NORMAL and cooldown expires

## Debouncing Strategy

### Purpose
Prevent rapid fluctuations from triggering multiple alerts.

### Implementation
```python
class AnomalyDetector:
    def __init__(self):
        self.states = {
            'cpu': AnomalyState(),
            'memory': AnomalyState(),
            'process': AnomalyState(),
            'disk': AnomalyState(),
        }
    
    def check_anomaly(self, metric_type: str, value: float, threshold: float) -> Optional[AnomalyEvent]:
        state = self.states[metric_type]
        now = time.time()
        
        if value > threshold:
            if state.status == 'NORMAL':
                state.status = 'POTENTIAL'
                state.start_time = now
            elif state.status == 'POTENTIAL':
                if now - state.start_time >= state.duration_threshold:
                    state.status = 'CONFIRMED'
                    return self.create_event(metric_type, value)
        else:
            # Value dropped below threshold
            if state.status in ('ACKNOWLEDGED',):
                if now - state.ack_time >= state.cooldown:
                    state.status = 'NORMAL'
            else:
                state.status = 'NORMAL'
        
        return None
```

### Duration Thresholds
- **CPU**: 3 seconds
- **Memory**: 5 seconds
- **Process**: 5 seconds
- **Disk**: 10 seconds

## Event Generation

### Anomaly Event Structure
```python
@dataclass
class AnomalyEvent:
    """Anomaly event to trigger AI suggestion."""
    id: str  # Unique event ID
    type: str  # 'cpu', 'memory', 'process', 'disk'
    timestamp: float
    severity: str  # ' warning', 'critical', 'info'
    
    # Metrics at time of detection
    metrics: Dict[str, Any]
    
    # Related process (if applicable)
    related_process: Optional[ProcessInfo] = None
    
    # Event metadata
    is_sustained: bool = True  # Has been sustained for required duration
    duration_seconds: float = 0.0  # How long anomaly has persisted
```

### Event Examples

#### CPU Anomaly Event
```python
AnomalyEvent(
    id="cpu_20260109_010630_001",
    type="cpu",
    timestamp=1736356590.123,
    severity="critical",
    metrics={
        "cpu_percent": 95.5,
        "per_core": [98, 92, 96, 94],
    },
    related_process=ProcessInfo(
        pid=1234,
        name="Chrome",
        cpu_percent=60.5,
        memory_percent=15.2,
        status="running"
    ),
    is_sustained=True,
    duration_seconds=5.2
)
```

#### Memory Anomaly Event
```python
AnomalyEvent(
    id="memory_20260109_010635_001",
    type="memory",
    timestamp=1736356595.456,
    severity="warning",
    metrics={
        "memory_percent": 92.3,
        "memory_used_gb": 14.8,
        "memory_total_gb": 16.0,
    },
    related_process=ProcessInfo(
        pid=5678,
        name="Photoshop",
        cpu_percent=5.2,
        memory_percent=45.8,
        status="running"
    ),
    is_sustained=True,
    duration_seconds=7.1
)
```

## Filtering Strategy

### Deduplication
Avoid creating duplicate events:
- Check if recent event (< 60s) exists for same type
- Compare metric values (must differ by > 10%)
- Skip if duplicate detected

### Prioritization
When multiple anomalies occur:
1. **Critical** severity first
2. **Warning** severity second
3. **Info** severity last
4. Tie-breaker: Most recent event

### Suppression Rules
Don't trigger events for:
- Expected behavior (e.g., Time Machine backup → high disk I/O)
- System processes (kernel_task, WindowServer)
- Short-lived spikes (< duration threshold)

## Integration with Monitoring

### Data Flow
```
SystemMonitor (QThread)
    ↓ (emits system_data_updated signal every 1s)
AnomalyDetector
    ↓ (analyzes metrics)
    ↓ (generates AnomalyEvent if threshold crossed and sustained)
SuggestionEngine (QThread)
    ↓ (receives event via queue)
    ↓ (calls AI for suggestion)
UI (MainWindow)
    ↓ (displays suggestion in AIWidget)
```

### Signal/Slot Connections
```python
# In app.py
self.system_monitor.system_data_updated.connect(
    self.anomaly_detector.check_system_data
)

self.anomaly_detector.anomaly_detected.connect(
    self.suggestion_engine.handle_anomaly
)

self.suggestion_engine.suggestion_ready.connect(
    self.main_window.ai_widget.show_suggestion
)
```

## Testing Strategy

### Unit Tests
Test each anomaly type:
- Normal values (no anomaly)
- Threshold barely crossed (no event - not sustained)
- Sustained anomaly (event generated)
- Rapid fluctuations (debouncing works)
- Cooldown period (no duplicate events)

### Test Cases

#### Test Case 1: CPU Sustained Anomaly
```python
def test_cpu_sustained_anomaly():
    detector = AnomalyDetector()
    
    # T+0s: Normal
    assert detector.check('cpu', 70, threshold=80) is None
    
    # T+1s: Crosses threshold
    time.sleep(1)
    assert detector.check('cpu', 85, threshold=80) is None  # Not sustained yet
    
    # T+4s: Sustained > 3s
    time.sleep(3)
    event = detector.check('cpu', 85, threshold=80)
    assert event is not None
    assert event.type == 'cpu'
    assert event.severity == 'warning'
```

#### Test Case 2: Memory Fluctuation (Debouncing)
```python
def test_memory_fluctuation():
    detector = AnomalyDetector()
    
    # Spike up
    detector.check('memory', 91, threshold=90)
    time.sleep(2)
    
    # Drop back down before duration threshold (5s)
    assert detector.check('memory', 85, threshold=90) is None
    
    # No event should be generated
    assert detector.states['memory'].status == 'NORMAL'
```

#### Test Case 3: Cooldown Period
```python
def test_cooldown_period():
    detector = AnomalyDetector()
    
    # Generate first event
    detector.states['cpu'].status = 'CONFIRMED'
    event1 = detector.check('cpu', 95, threshold=80)
    assert event1 is not None
    
    # Mark as acknowledged
    detector.states['cpu'].status = 'ACKNOWLEDGED'
    detector.states['cpu'].ack_time = time.time()
    
    # Immediate re-check (still high) - should not generate new event
    event2 = detector.check('cpu', 95, threshold=80)
    assert event2 is None
    
    # After cooldown (60s) - should generate new event
    detector.states['cpu'].ack_time = time.time() - 65
    detector.check('cpu', 75, threshold=80)  # Drop below
    event3 = detector.check('cpu', 95, threshold=80)  # Rise again
    time.sleep(4)
    event3 = detector.check('cpu', 95, threshold=80)
    assert event3 is not None
```

## Configuration

### Adjustable Parameters
All thresholds and durations configurable via `config.py`:

```python
class AnomalyConfig(BaseModel):
    cpu_threshold: float = 80.0
    cpu_duration_seconds: float = 3.0
    cpu_cooldown_seconds: float = 60.0
    
    memory_threshold: float = 90.0
    memory_duration_seconds: float = 5.0
    memory_cooldown_seconds: float = 60.0
    
    process_cpu_threshold: float = 50.0
    process_memory_threshold: float = 50.0
    process_duration_seconds: float = 5.0
    process_cooldown_seconds: float = 60.0
    
    disk_io_threshold_mb_per_sec: float = 200.0
    disk_duration_seconds: float = 10.0
    disk_cooldown_seconds: float = 120.0  # Longer cooldown for disk
```

### Runtime Adjustment
Allow users to adjust sensitivity:
- **Strict**: Lower thresholds, shorter durations
- **Balanced**: Default values
- **Relaxed**: Higher thresholds, longer durations

## Edge Cases

### System Startup
- First 30 seconds: Suppress all anomalies
- System warming up, many processes starting
- Wait for stable baseline

### Sleep/Wake
- After wake: Reset all anomaly states
- Metrics may spike temporarily
- Wait 10 seconds before detecting

### Low Resource Systems
- On systems with < 8GB RAM:
  - Lower memory threshold to 85%
- On dual-core CPUs:
  - Lower CPU threshold to 70%

## Performance Impact

### Detection Overhead
- Runs once per second (with monitoring loop)
- Lightweight comparisons only
- Target: < 0.1ms per detection cycle

### Memory Footprint
- State tracking: Minimal (4 states × ~100 bytes)
- Event history: Keep last 10 events only
- Total: < 1MB

## Future Enhancements

### Machine Learning
- Learn normal usage patterns
- Dynamic thresholds based on history
- Anomaly detection via statistical models

### Predictive Alerts
- Detect trends before threshold crossed
- "Memory usage rising rapidly" warnings

### User Feedback
- Allow users to dismiss false positives
- Train system to ignore specific scenarios
