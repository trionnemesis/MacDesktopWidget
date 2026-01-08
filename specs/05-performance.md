# Performance Requirements Specification

## Overview

This document defines performance requirements and optimization strategies for MacDesktopWidget.

## Performance Targets

### CPU Overhead
- **Target**: < 2% CPU usage (average)
- **Peak**: < 5% CPU during AI inference
- **Idle**: < 1% CPU when no anomalies
- **Measurement**: Monitor own process via psutil

### Memory Footprint
- **Target**: < 100MB total RAM usage
- **Breakdown**:
  - Monitoring subsystem: < 50MB
  - UI subsystem: < 30MB
  - AI subsystem: < 20MB
- **Peak**: < 150MB during AI inference

### Update Latency
- **UI Refresh**: Every 1000ms ± 50ms
- **Monitoring Collection**: Complete in < 100ms
- **Anomaly Detection**: < 10ms per cycle
- **AI Suggestion**: < 2000ms from anomaly to display

### Startup Time
- **Target**: Application ready in < 3 seconds
- **Breakdown**:
  - Config load: < 100ms
  - UI initialization: < 1000ms
  - Monitoring start: < 500ms
  - Ollama health check: < 1000ms (async, non-blocking)

### Responsiveness
- **UI Interactions**: < 16ms (60 FPS)
- **Drag-to-move**: Smooth, no lag
- **Click response**: Immediate (<100ms)

## Optimization Strategies

### Monitoring Optimization

#### Efficient Data Collection
```python
# GOOD: Reuse psutil calls
cpu_times = psutil.cpu_times_percent(interval=None)  # Non-blocking
cpu_percent = psutil.cpu_percent(interval=None)

# BAD: Blocking calls
cpu_percent = psutil.cpu_percent(interval=1.0)  # Blocks for 1 second!
```

#### Batched Process Collection
```python
# Collect all process data in single iteration
processes = []
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
    try:
        info = proc.info
        processes.append(ProcessInfo(**info))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

# Sort once
top_cpu = sorted(processes, key=lambda p: p.cpu_percent, reverse=True)[:10]
top_mem = sorted(processes, key=lambda p: p.memory_percent, reverse=True)[:10]
```

#### Avoid Redundant Calls
```python
# Cache disk partitions list (doesn't change frequently)
@lru_cache(maxsize=1)
def get_disk_partitions():
    return psutil.disk_partitions()

# Refresh cache every 60 seconds
def refresh_partitions_cache():
    get_disk_partitions.cache_clear()
```

### UI Optimization

#### Minimize Repaints
```python
# Update only changed values
def update_cpu_display(self, new_value: float):
    if abs(new_value - self.current_value) < 1.0:
        return  # Skip update for < 1% change
    
    self.current_value = new_value
    self.update()  # Trigger repaint
```

#### Use QTimer Correctly
```python
# GOOD: Single timer for all updates
self.update_timer = QTimer()
self.update_timer.timeout.connect(self.update_all_widgets)
self.update_timer.start(1000)

# BAD: Multiple timers
self.cpu_timer.start(1000)
self.memory_timer.start(1000)  # Creates unnecessary overhead
```

#### Optimize Transparency Rendering
```python
# Set window attributes once
self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

# Use hardware acceleration
self.setAttribute(Qt.WidgetAttribute.WA_AcceleratedCompositing)
```

### Threading Optimization

#### Thread Pool Management
```python
# Limit concurrent threads
MAX_THREADS = 3  # Monitoring, AI, Background tasks

# Use QThreadPool for worker tasks
pool = QThreadPool.globalInstance()
pool.setMaxThreadCount(MAX_THREADS)
```

#### Avoid Thread Starvation
```python
# Priority levels for tasks
class MonitorTask(QRunnable):
    def run(self):
        QThread.currentThread().setPriority(QThread.Priority.HighPriority)
        # Monitoring is time-sensitive

class AITask(QRunnable):
    def run(self):
        QThread.currentThread().setPriority(QThread.Priority.NormalPriority)
        # AI can tolerate slight delays
```

### AI Optimization

#### Async Non-Blocking Calls
```python
# Use async/await for Ollama API
async def get_ai_suggestion(context: Dict) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=5)
        ) as response:
            result = await response.json()
            return result['response']
```

#### Request Caching
```python
# Cache suggestions by anomaly signature
cache = TTLCache(maxsize=100, ttl=60)  # 60 second TTL

def get_cached_suggestion(anomaly_signature: str) -> Optional[str]:
    return cache.get(anomaly_signature)

def cache_suggestion(anomaly_signature: str, suggestion: str):
    cache[anomaly_signature] = suggestion
```

#### Rate Limiting
```python
# Prevent AI API spam
last_request_time = 0
MIN_REQUEST_INTERVAL = 10  # seconds

async def request_ai_suggestion(context: Dict) -> str:
    global last_request_time
    now = time.time()
    
    if now - last_request_time < MIN_REQUEST_INTERVAL:
        return get_fallback_suggestion(context)
    
    last_request_time = now
    return await get_ai_suggestion(context)
```

## Resource Monitoring

### Self-Monitoring
Monitor the widget's own resource usage:

```python
class SelfMonitor:
    """Monitor the application's own resource usage."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
    
    def get_own_cpu(self) -> float:
        """Get CPU usage of this process."""
        return self.process.cpu_percent(interval=None)
    
    def get_own_memory(self) -> int:
        """Get memory usage in bytes."""
        return self.process.memory_info().rss
    
    def check_limits(self) -> bool:
        """Check if we're exceeding performance targets."""
        cpu = self.get_own_cpu()
        mem_mb = self.get_own_memory() / 1024 / 1024
        
        if cpu > 5.0:
            logger.warning(f"High CPU overhead: {cpu:.1f}%")
        
        if mem_mb > 150:
            logger.warning(f"High memory usage: {mem_mb:.1f}MB")
        
        return cpu <= 5.0 and mem_mb <= 150
```

### Performance Logging
```python
import time
from functools import wraps

def log_performance(func):
    """Decorator to log function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        
        if elapsed > 100:  # Log if > 100ms
            logger.debug(f"{func.__name__} took {elapsed:.1f}ms")
        
        return result
    return wrapper

@log_performance
def collect_system_data() -> SystemData:
    # ... collection logic
    pass
```

## Profiling Strategy

### CPU Profiling
```python
# Use cProfile for CPU profiling
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run application...

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

### Memory Profiling
```python
# Use memory_profiler
from memory_profiler import profile

@profile
def collect_all_monitoring_data():
    # ... monitoring logic
    pass
```

### Continuous Profiling
```python
# Periodic performance checks
def performance_check(self):
    """Run every 60 seconds to check performance."""
    own_cpu = self.self_monitor.get_own_cpu()
    own_mem = self.self_monitor.get_own_memory() / 1024 / 1024
    
    metrics = {
        "cpu_percent": own_cpu,
        "memory_mb": own_mem,
        "timestamp": time.time()
    }
    
    # Log to performance log file
    with open("performance.log", "a") as f:
        f.write(json.dumps(metrics) + "\n")
```

## Load Testing

### Stress Test Scenarios

#### Scenario 1: Rapid Anomalies
- Simulate CPU spikes every 5 seconds
- Verify AI requests are rate-limited
- Check memory doesn't accumulate

#### Scenario 2: Long Running
- Run for 24 hours continuously
- Check for memory leaks
- Verify performance remains stable

#### Scenario 3: High Process Count
- System with 200+ processes
- Verify process collection < 100ms
- Check UI remains responsive

### Test Script Example
```python
import pytest
import time

def test_monitoring_performance():
    """Test monitoring completes within time budget."""
    monitor = SystemMonitor()
    
    durations = []
    for _ in range(100):  # 100 iterations
        start = time.perf_counter()
        monitor.collect_data()
        elapsed = time.perf_counter() - start
        durations.append(elapsed)
    
    avg_duration = sum(durations) / len(durations)
    max_duration = max(durations)
    
    assert avg_duration < 0.1, f"Average collection time {avg_duration:.3f}s exceeds 100ms"
    assert max_duration < 0.2, f"Max collection time {max_duration:.3f}s exceeds 200ms"
```

## Platform-Specific Optimizations

### macOS
- Use native macOS APIs where possible for GPU
- Leverage Core Graphics acceleration for UI
- Use Grand Central Dispatch for threading (if using Objective-C bindings)

### Windows (Development)
- Disable GPU monitoring (not supported)
- Use Windows-specific psutil optimizations
- Test transparency performance (may differ from macOS)

## Degradation Strategy

### Graceful Degradation
If performance targets not met:

1. **Reduce Update Frequency**: 1000ms → 2000ms
2. **Disable Animations**: Remove smooth transitions
3. **Reduce Process Count**: Top 10 → Top 5
4. **Disable AI**: Use template suggestions only

### Auto-Detection
```python
def adjust_performance_mode(self):
    """Automatically adjust performance settings."""
    cpu = self.self_monitor.get_own_cpu()
    
    if cpu > 5.0:
        # High CPU - reduce update frequency
        self.update_interval = 2000
        logger.info("Switched to 2-second updates due to high CPU")
    
    if cpu > 10.0:
        # Very high - disable animations
        self.animations_enabled = False
        logger.warning("Disabled animations due to excessive CPU")
```

## Testing Requirements

### Performance Tests
- All marked with `@pytest.mark.slow`
- Run separately from unit tests
- Measure actual metrics, not mocks

### Benchmarking Suite
- CPU overhead benchmark
- Memory footprint benchmark
- UI responsiveness benchmark
- End-to-end latency benchmark

### CI/CD Integration
- Run performance tests on each release
- Track metrics over time
- Alert if regressions detected

## Documentation

### Performance Guide
Create user-facing documentation:
- Expected resource usage
- How to reduce overhead (disable AI, increase interval)
- Troubleshooting slow performance

### Developer Guide
- Profiling techniques
- Optimization patterns
- Performance testing procedures
