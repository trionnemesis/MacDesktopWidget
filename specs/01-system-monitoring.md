# System Monitoring Specification

## Overview

This document specifies the system monitoring requirements for the MacDesktopWidget application.

## Data Collection Requirements

### CPU Monitoring
- **Metric**: Overall CPU utilization percentage
- **Per-core**: Individual core utilization percentages
- **Frequency**: Current CPU frequency (if available)
- **Data Source**: `psutil.cpu_percent()`, `psutil.cpu_freq()`
- **Update Interval**: 1 second

### Memory Monitoring
- **Total Memory**: Total physical RAM
- **Used Memory**: Currently used RAM
- **Available Memory**: Available RAM
- **Memory Percentage**: Used/Total * 100
- **Swap Memory**: Swap usage statistics
- **Data Source**: `psutil.virtual_memory()`, `psutil.swap_memory()`
- **Update Interval**: 1 second

### Disk I/O Monitoring
- **Read Rate**: Bytes read per second
- **Write Rate**: Bytes written per second
- **Disk Usage**: Used/Total space per partition
- **I/O Counters**: Read/write operation counts
- **Data Source**: `psutil.disk_io_counters()`, `psutil.disk_usage()`
- **Update Interval**: 1 second

### GPU Monitoring (macOS)
- **GPU Utilization**: Percentage (0-100%)
- **GPU Memory**: Used/Total VRAM
- **Data Source**: `macmon` library (primary), fallback to `system_profiler`
- **Platform**: macOS only (may not be available on all systems)
- **Fallback**: Display "N/A" if GPU monitoring unavailable

### Process Monitoring
- **Top Processes**: Top 10 by CPU and Memory usage
- **Process Info**: PID, name, CPU%, Memory%, status
- **Data Source**: `psutil.process_iter()`
- **Update Interval**: 1 second
- **Sorting**: Separate lists for CPU and Memory

## Threading Model

### Main Thread
- **Responsibility**: UI rendering and event handling
- **Constraints**: Must remain responsive at all times
- **No blocking operations**: All monitoring happens in background threads

### Monitoring Thread (QThread)
- **Class**: `SystemMonitor` (inherits from `QThread`)
- **Responsibility**: Orchestrate all monitoring tasks
- **Update Cycle**: 1000ms (configurable via `MonitoringConfig.update_interval_ms`)
- **Signal Emission**: Emit `system_data_updated` signal with aggregated data

### Sub-monitoring Tasks
Each monitor runs as part of the main monitoring thread:
- `CPUMonitor`
- `MemoryMonitor`
- `DiskMonitor`
- `GPUMonitor` (with error handling for unavailability)
- `ProcessMonitor`

### Thread Safety
- Use Qt signals/slots for thread communication
- No shared mutable state between threads
- Immutable data structures for passing data

## Data Structures

### SystemData
```python
@dataclass
class SystemData:
    timestamp: float
    cpu: CPUData
    memory: MemoryData
    disk: DiskData
    gpu: Optional[GPUData]
    processes: ProcessData
```

### CPUData
```python
@dataclass
class CPUData:
    total_percent: float
    per_core_percent: List[float]
    frequency_mhz: Optional[float]
```

### MemoryData
```python
@dataclass
class MemoryData:
    total_bytes: int
    used_bytes: int
    available_bytes: int
    percent: float
    swap_used_bytes: int
    swap_total_bytes: int
```

### DiskData
```python
@dataclass
class DiskData:
    read_bytes_per_sec: float
    write_bytes_per_sec: float
    partitions: Dict[str, PartitionInfo]
```

### GPUData
```python
@dataclass
class GPUData:
    utilization_percent: Optional[float]
    memory_used_bytes: Optional[int]
    memory_total_bytes: Optional[int]
    available: bool
```

### ProcessData
```python
@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str

@dataclass
class ProcessData:
    top_by_cpu: List[ProcessInfo]  # Top 10
    top_by_memory: List[ProcessInfo]  # Top 10
```

## Error Handling

### Collection Errors
- **Action**: Log error and continue with best-effort data
- **Missing Data**: Use `None` or default values
- **User Notification**: Do not show collection errors to user

### GPU Monitoring Failures
- **Expected**: GPU monitoring may not work on all systems
- **Fallback**: Set `GPUData.available = False`
- **UI Display**: Show "GPU monitoring unavailable" message

### Process Access Errors
- **Common**: Some processes may deny access
- **Action**: Skip inaccessible processes silently
- **Logging**: Log at DEBUG level only

## Performance Considerations

### CPU Overhead Target
- **Target**: < 2% CPU usage for monitoring
- **Measurement**: Monitor the monitor (check own CPU usage)
- **Optimization**: Use efficient psutil calls, avoid redundant data collection

### Memory Footprint
- **Target**: < 50MB for monitoring subsystem
- **Strategy**: Reuse data structures, avoid accumulation
- **Cleanup**: Clear old process lists each cycle

### Update Latency
- **Target**: Complete all monitoring in < 100ms
- **Timeout**: Individual monitor operations timeout at 50ms
- **Graceful Degradation**: Skip slow operations if timeout exceeded

## Platform-Specific Considerations

### macOS
- Primary target platform
- GPU monitoring via `macmon` library
- Full feature support

### Windows (Development Environment)
- CPU, Memory, Disk, Process monitoring work via `psutil`
- GPU monitoring unavailable (graceful fallback)
- Can be used for development and testing of core features

### Linux (Future)
- Not currently supported
- All monitoring would work except GPU
- Can be added in future versions

## Testing Requirements

### Unit Tests
- Mock `psutil` calls for reproducible tests
- Test each monitor class independently
- Verify data structure correctness
- Test error handling paths

### Integration Tests
- Test full monitoring cycle
- Verify signal emission
- Test thread lifecycle (start/stop/cleanup)

### Performance Tests
- Measure actual CPU overhead
- Measure memory footprint
- Verify update frequency accuracy
