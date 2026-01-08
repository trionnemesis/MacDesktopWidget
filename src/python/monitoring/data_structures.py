"""
Data structures for system monitoring.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class ProcessStatus(str, Enum):
    """Process status enum."""
    RUNNING = "running"
    SLEEPING = "sleeping"
    DISK_SLEEP = "disk_sleep" 
    STOPPED = "stopped"
    ZOMBIE = "zombie"
    UNKNOWN = "unknown"


@dataclass
class CPUData:
    """CPU monitoring data."""
    total_percent: float
    per_core_percent: List[float]
    frequency_mhz: Optional[float] = None
    
    def __post_init__(self):
        """Validate data."""
        assert 0 <= self.total_percent <= 100
        assert all(0 <= p <= 100 for p in self.per_core_percent)


@dataclass
class MemoryData:
    """Memory monitoring data."""
    total_bytes: int
    used_bytes: int
    available_bytes: int
    percent: float
    swap_used_bytes: int = 0
    swap_total_bytes: int = 0
    
    def __post_init__(self):
        """Validate data."""
        assert self.total_bytes > 0
        assert 0 <= self.percent <= 100
    
    @property
    def used_gb(self) -> float:
        """Used memory in GB."""
        return self.used_bytes / (1024 ** 3)
    
    @property
    def total_gb(self) -> float:
        """Total memory in GB."""
        return self.total_bytes / (1024 ** 3)


@dataclass
class PartitionInfo:
    """Disk partition information."""
    mountpoint: str
    fstype: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    percent: float


@dataclass
class DiskData:
    """Disk I/O monitoring data."""
    read_bytes_per_sec: float
    write_bytes_per_sec: float
    partitions: Dict[str, PartitionInfo] = field(default_factory=dict)
    
    @property
    def read_mb_per_sec(self) -> float:
        """Read speed in MB/s."""
        return self.read_bytes_per_sec / (1024 ** 2)
    
    @property
    def write_mb_per_sec(self) -> float:
        """Write speed in MB/s."""
        return self.write_bytes_per_sec / (1024 ** 2)


@dataclass
class GPUData:
    """GPU monitoring data."""
    utilization_percent: Optional[float] = None
    memory_used_bytes: Optional[int] = None
    memory_total_bytes: Optional[int] = None
    available: bool = False
    error_message: Optional[str] = None
    
    @property
    def memory_used_gb(self) -> Optional[float]:
        """GPU memory used in GB."""
        if self.memory_used_bytes is not None:
            return self.memory_used_bytes / (1024 ** 3)
        return None
    
    @property
    def memory_total_gb(self) -> Optional[float]:
        """GPU total memory in GB."""
        if self.memory_total_bytes is not None:
            return self.memory_total_bytes / (1024 ** 3)
        return None


@dataclass
class ProcessInfo:
    """Process information."""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str = "unknown"
    memory_bytes: int = 0
    
    @property
    def memory_mb(self) -> float:
        """Memory usage in MB."""
        return self.memory_bytes / (1024 ** 2)


@dataclass
class ProcessData:
    """Process monitoring data."""
    top_by_cpu: List[ProcessInfo] = field(default_factory=list)
    top_by_memory: List[ProcessInfo] = field(default_factory=list)
    total_processes: int = 0


@dataclass
class NetworkIOCounters:
    """Network I/O counters."""
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int = 0
    errout: int = 0
    dropin: int = 0
    dropout: int = 0


@dataclass
class ProcessNetworkInfo:
    """Process network usage information."""
    pid: int
    name: str
    upload_bytes_per_sec: float
    download_bytes_per_sec: float
    connections_count: int = 0

    @property
    def upload_mb_per_sec(self) -> float:
        """Upload speed in MB/s."""
        return self.upload_bytes_per_sec / (1024 ** 2)

    @property
    def download_mb_per_sec(self) -> float:
        """Download speed in MB/s."""
        return self.download_bytes_per_sec / (1024 ** 2)

    @property
    def total_mb_per_sec(self) -> float:
        """Total network speed in MB/s."""
        return (self.upload_bytes_per_sec + self.download_bytes_per_sec) / (1024 ** 2)


@dataclass
class NetworkData:
    """Network monitoring data."""
    upload_bytes_per_sec: float
    download_bytes_per_sec: float
    io_counters: NetworkIOCounters
    top_processes: List[ProcessNetworkInfo] = field(default_factory=list)

    @property
    def upload_mb_per_sec(self) -> float:
        """Upload speed in MB/s."""
        return self.upload_bytes_per_sec / (1024 ** 2)

    @property
    def download_mb_per_sec(self) -> float:
        """Download speed in MB/s."""
        return self.download_bytes_per_sec / (1024 ** 2)

    @property
    def total_mb_per_sec(self) -> float:
        """Total network speed in MB/s."""
        return (self.upload_bytes_per_sec + self.download_bytes_per_sec) / (1024 ** 2)


@dataclass
class BatteryData:
    """Battery monitoring data."""
    percent: float
    is_charging: bool
    time_remaining_seconds: Optional[int] = None
    health_percent: Optional[int] = None
    cycle_count: Optional[int] = None
    condition: Optional[str] = None

    @property
    def time_remaining_hours(self) -> Optional[float]:
        """Time remaining in hours."""
        if self.time_remaining_seconds is not None and self.time_remaining_seconds > 0:
            return self.time_remaining_seconds / 3600
        return None


@dataclass
class TemperatureData:
    """Temperature monitoring data."""
    cpu_temp: Optional[float] = None
    gpu_temp: Optional[float] = None
    avg_temp: Optional[float] = None
    max_temp: Optional[float] = None
    all_sensors: Dict[str, float] = field(default_factory=dict)


@dataclass
class SystemData:
    """Complete system monitoring data."""
    timestamp: float
    cpu: CPUData
    memory: MemoryData
    disk: DiskData
    gpu: Optional[GPUData]
    processes: ProcessData
    network: Optional[NetworkData] = None
    battery: Optional[BatteryData] = None
    temperature: Optional[TemperatureData] = None
