"""
Anomaly detection system for system monitoring.
"""
import time
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict
from enum import Enum
import hashlib

from .data_structures import SystemData, ProcessInfo

logger = logging.getLogger(__name__)


class AnomalyType(str, Enum):
    """Types of system anomalies."""
    CPU = "cpu"
    MEMORY = "memory"
    PROCESS_CPU = "process_cpu"
    PROCESS_MEMORY = "process_memory"
    DISK_IO = "disk_io"


class AnomalySeverity(str, Enum):
    """Severity levels for anomalies."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AnomalyStatus(str, Enum):
    """State machine status for anomaly tracking."""
    NORMAL = "normal"
    POTENTIAL = "potential"
    CONFIRMED = "confirmed"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class AnomalyEvent:
    """Anomaly event to trigger AI suggestion."""
    id: str
    type: AnomalyType
    timestamp: float
    severity: AnomalySeverity
    metrics: Dict[str, float]
    related_process: Optional[ProcessInfo] = None
    is_sustained: bool = True
    duration_seconds: float = 0.0
    
    def get_signature(self) -> str:
        """
        Get a signature for this anomaly for deduplication.
        
        Returns:
            Hash signature string.
        """
        # Create signature based on type and primary metric
        primary_value = self.metrics.get('primary_value', 0)
        # Round to nearest 10 to allow minor fluctuations
        rounded_value = int(primary_value / 10) * 10
        sig_string = f"{self.type}_{rounded_value}"
        
        if self.related_process:
            sig_string += f"_{self.related_process.name}"
        
        return hashlib.md5(sig_string.encode()).hexdigest()[:16]


@dataclass
class AnomalyState:
    """State tracking for a single anomaly type."""
    status: AnomalyStatus = AnomalyStatus.NORMAL
    start_time: float = 0.0
    ack_time: float = 0.0
    last_event_id: Optional[str] = None


class AnomalyDetector:
    """Detect system resource anomalies."""
    
    def __init__(
        self,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 90.0,
        process_threshold: float = 50.0,
        disk_io_threshold_mb: float = 200.0,
        cpu_duration: float = 3.0,
        memory_duration: float = 5.0,
        process_duration: float = 5.0,
        disk_duration: float = 10.0,
        cooldown: float = 60.0
    ):
        """
        Initialize anomaly detector.
        
        Args:
            cpu_threshold: CPU percentage threshold.
            memory_threshold: Memory percentage threshold.
            process_threshold: Single process resource threshold.
            disk_io_threshold_mb: Disk I/O threshold in MB/s.
            cpu_duration: Sustained duration for CPU anomaly (seconds).
            memory_duration: Sustained duration for memory anomaly (seconds).
            process_duration: Sustained duration for process anomaly (seconds).
            disk_duration: Sustained duration for disk anomaly (seconds).
            cooldown: Cooldown period after acknowledgment (seconds).
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.process_threshold = process_threshold
        self.disk_io_threshold_mb = disk_io_threshold_mb
        
        self.durations = {
            AnomalyType.CPU: cpu_duration,
            AnomalyType.MEMORY: memory_duration,
            AnomalyType.PROCESS_CPU: process_duration,
            AnomalyType.PROCESS_MEMORY: process_duration,
            AnomalyType.DISK_IO: disk_duration,
        }
        
        self.cooldown = cooldown
        
        # State tracking for each anomaly type
        self.states: Dict[AnomalyType, AnomalyState] = {
            atype: AnomalyState() for atype in AnomalyType
        }
        
        # Event cache for deduplication
        self.recent_events: Dict[str, float] = {}  # signature -> timestamp
        
        logger.info("Anomaly Detector initialized")
    
    def check_system_data(self, system_data: SystemData) -> list[AnomalyEvent]:
        """
        Check system data for anomalies.
        
        Args:
            system_data: Current system monitoring data.
        
        Returns:
            List of new anomaly events (may be empty).
        """
        events = []
        now = time.time()
        
        # Clean up old event signatures
        self._cleanup_event_cache(now)
        
        # Check CPU
        cpu_event = self._check_cpu(system_data, now)
        if cpu_event:
            events.append(cpu_event)
        
        # Check Memory
        memory_event = self._check_memory(system_data, now)
        if memory_event:
            events.append(memory_event)
        
        # Check high-resource processes
        process_events = self._check_processes(system_data, now)
        events.extend(process_events)
        
        # Check Disk I/O
        disk_event = self._check_disk_io(system_data, now)
        if disk_event:
            events.append(disk_event)
        
        return events
    
    def _check_cpu(self, system_data: SystemData, now: float) -> Optional[AnomalyEvent]:
        """Check for CPU anomalies."""
        cpu_percent = system_data.cpu.total_percent
        threshold = self.cpu_threshold
        anomaly_type = AnomalyType.CPU
        
        state = self.states[anomaly_type]
        
        if cpu_percent > threshold:
            if state.status == AnomalyStatus.NORMAL:
                state.status = AnomalyStatus.POTENTIAL
                state.start_time = now
                logger.debug(f"CPU anomaly potential: {cpu_percent:.1f}%")
            
            elif state.status == AnomalyStatus.POTENTIAL:
                duration = now - state.start_time
                if duration >= self.durations[anomaly_type]:
                    state.status = AnomalyStatus.CONFIRMED
                    return self._create_cpu_event(system_data, now, duration)
        
        else:
            # CPU dropped below threshold
            if state.status == AnomalyStatus.ACKNOWLEDGED:
                if now - state.ack_time >= self.cooldown:
                    state.status = AnomalyStatus.NORMAL
                    logger.debug("CPU anomaly cleared after cooldown")
            else:
                state.status = AnomalyStatus.NORMAL
        
        return None
    
    def _check_memory(self, system_data: SystemData, now: float) -> Optional[AnomalyEvent]:
        """Check for memory anomalies."""
        memory_percent = system_data.memory.percent
        threshold = self.memory_threshold
        anomaly_type = AnomalyType.MEMORY
        
        state = self.states[anomaly_type]
        
        if memory_percent > threshold:
            if state.status == AnomalyStatus.NORMAL:
                state.status = AnomalyStatus.POTENTIAL
                state.start_time = now
                logger.debug(f"Memory anomaly potential: {memory_percent:.1f}%")
            
            elif state.status == AnomalyStatus.POTENTIAL:
                duration = now - state.start_time
                if duration >= self.durations[anomaly_type]:
                    state.status = AnomalyStatus.CONFIRMED
                    return self._create_memory_event(system_data, now, duration)
        
        else:
            if state.status == AnomalyStatus.ACKNOWLEDGED:
                if now - state.ack_time >= self.cooldown:
                    state.status = AnomalyStatus.NORMAL
                    logger.debug("Memory anomaly cleared after cooldown")
            else:
                state.status = AnomalyStatus.NORMAL
        
        return None
    
    def _check_processes(self, system_data: SystemData, now: float) -> list[AnomalyEvent]:
        """Check for high-resource process anomalies."""
        events = []
        
        # Check top CPU process
        if system_data.processes.top_by_cpu:
            top_cpu_proc = system_data.processes.top_by_cpu[0]
            if top_cpu_proc.cpu_percent > self.process_threshold:
                event = self._check_single_process_anomaly(
                    top_cpu_proc,
                    AnomalyType.PROCESS_CPU,
                    top_cpu_proc.cpu_percent,
                    now
                )
                if event:
                    events.append(event)
        
        # Check top memory process
        if system_data.processes.top_by_memory:
            top_mem_proc = system_data.processes.top_by_memory[0]
            if top_mem_proc.memory_percent > self.process_threshold:
                event = self._check_single_process_anomaly(
                    top_mem_proc,
                    AnomalyType.PROCESS_MEMORY,
                    top_mem_proc.memory_percent,
                    now
                )
                if event:
                    events.append(event)
        
        return events
    
    def _check_single_process_anomaly(
        self,
        process: ProcessInfo,
        anomaly_type: AnomalyType,
        value: float,
        now: float
    ) -> Optional[AnomalyEvent]:
        """Check for a single process anomaly."""
        state = self.states[anomaly_type]
        
        if state.status == AnomalyStatus.NORMAL:
            state.status = AnomalyStatus.POTENTIAL
            state.start_time = now
            logger.debug(f"Process anomaly potential: {process.name} ({value:.1f}%)")
        
        elif state.status == AnomalyStatus.POTENTIAL:
            duration = now - state.start_time
            if duration >= self.durations[anomaly_type]:
                state.status = AnomalyStatus.CONFIRMED
                return self._create_process_event(process, anomaly_type, now, duration)
        
        # Note: Process anomalies don't track ACKNOWLEDGED state per process
        # as processes are more dynamic
        
        return None
    
    def _check_disk_io(self, system_data: SystemData, now: float) -> Optional[AnomalyEvent]:
        """Check for disk I/O anomalies."""
        read_mb = system_data.disk.read_mb_per_sec
        write_mb = system_data.disk.write_mb_per_sec
        max_io = max(read_mb, write_mb)
        
        threshold = self.disk_io_threshold_mb
        anomaly_type = AnomalyType.DISK_IO
        
        state = self.states[anomaly_type]
        
        if max_io > threshold:
            if state.status == AnomalyStatus.NORMAL:
                state.status = AnomalyStatus.POTENTIAL
                state.start_time = now
                logger.debug(f"Disk I/O anomaly potential: {max_io:.1f} MB/s")
            
            elif state.status == AnomalyStatus.POTENTIAL:
                duration = now - state.start_time
                if duration >= self.durations[anomaly_type]:
                    state.status = AnomalyStatus.CONFIRMED
                    return self._create_disk_event(system_data, now, duration)
        
        else:
            if state.status == AnomalyStatus.ACKNOWLEDGED:
                if now - state.ack_time >= self.cooldown:
                    state.status = AnomalyStatus.NORMAL
                    logger.debug("Disk I/O anomaly cleared after cooldown")
            else:
                state.status = AnomalyStatus.NORMAL
        
        return None
    
    def _create_cpu_event(
        self,
        system_data: SystemData,
        now: float,
        duration: float
    ) -> AnomalyEvent:
        """Create CPU anomaly event."""
        cpu_percent = system_data.cpu.total_percent
        
        # Get top CPU process
        top_process = None
        if system_data.processes.top_by_cpu:
            top_process = system_data.processes.top_by_cpu[0]
        
        severity = AnomalySeverity.CRITICAL if cpu_percent > 90 else AnomalySeverity.WARNING
        
        event = AnomalyEvent(
            id=f"cpu_{int(now)}",
            type=AnomalyType.CPU,
            timestamp=now,
            severity=severity,
            metrics={
                "cpu_percent": cpu_percent,
                "primary_value": cpu_percent,
            },
            related_process=top_process,
            is_sustained=True,
            duration_seconds=duration
        )
        
        # Mark as acknowledged and record event
        self.states[AnomalyType.CPU].status = AnomalyStatus.ACKNOWLEDGED
        self.states[AnomalyType.CPU].ack_time = now
        self.recent_events[event.get_signature()] = now
        
        logger.info(f"CPU anomaly detected: {cpu_percent:.1f}%")
        return event
    
    def _create_memory_event(
        self,
        system_data: SystemData,
        now: float,
        duration: float
    ) -> AnomalyEvent:
        """Create memory anomaly event."""
        memory_percent = system_data.memory.percent
        
        # Get top memory process
        top_process = None
        if system_data.processes.top_by_memory:
            top_process = system_data.processes.top_by_memory[0]
        
        severity = AnomalySeverity.CRITICAL if memory_percent > 95 else AnomalySeverity.WARNING
        
        event = AnomalyEvent(
            id=f"memory_{int(now)}",
            type=AnomalyType.MEMORY,
            timestamp=now,
            severity=severity,
            metrics={
                "memory_percent": memory_percent,
                "memory_used_gb": system_data.memory.used_gb,
                "memory_total_gb": system_data.memory.total_gb,
                "primary_value": memory_percent,
            },
            related_process=top_process,
            is_sustained=True,
            duration_seconds=duration
        )
        
        self.states[AnomalyType.MEMORY].status = AnomalyStatus.ACKNOWLEDGED
        self.states[AnomalyType.MEMORY].ack_time = now
        self.recent_events[event.get_signature()] = now
        
        logger.info(f"Memory anomaly detected: {memory_percent:.1f}%")
        return event
    
    def _create_process_event(
        self,
        process: ProcessInfo,
        anomaly_type: AnomalyType,
        now: float,
        duration: float
    ) -> AnomalyEvent:
        """Create process anomaly event."""
        if anomaly_type == AnomalyType.PROCESS_CPU:
            primary_value = process.cpu_percent
            metric_name = "cpu_percent"
        else:
            primary_value = process.memory_percent
            metric_name = "memory_percent"
        
        severity = AnomalySeverity.CRITICAL if primary_value > 75 else AnomalySeverity.WARNING
        
        event = AnomalyEvent(
            id=f"process_{anomaly_type.value}_{int(now)}",
            type=anomaly_type,
            timestamp=now,
            severity=severity,
            metrics={
                metric_name: primary_value,
                "primary_value": primary_value,
            },
            related_process=process,
            is_sustained=True,
            duration_seconds=duration
        )
        
        # Process anomalies reset immediately (processes change frequently)
        self.states[anomaly_type].status = AnomalyStatus.NORMAL
        self.recent_events[event.get_signature()] = now
        
        logger.info(f"Process anomaly detected: {process.name} ({primary_value:.1f}%)")
        return event
    
    def _create_disk_event(
        self,
        system_data: SystemData,
        now: float,
        duration: float
    ) -> AnomalyEvent:
        """Create disk I/O anomaly event."""
        read_mb = system_data.disk.read_mb_per_sec
        write_mb = system_data.disk.write_mb_per_sec
        max_io = max(read_mb, write_mb)
        
        event = AnomalyEvent(
            id=f"disk_io_{int(now)}",
            type=AnomalyType.DISK_IO,
            timestamp=now,
            severity=AnomalySeverity.INFO,  # Disk I/O is usually informational
            metrics={
                "read_mb_per_sec": read_mb,
                "write_mb_per_sec": write_mb,
                "max_io_mb_per_sec": max_io,
                "primary_value": max_io,
            },
            is_sustained=True,
            duration_seconds=duration
        )
        
        self.states[AnomalyType.DISK_IO].status = AnomalyStatus.ACKNOWLEDGED
        self.states[AnomalyType.DISK_IO].ack_time = now
        self.recent_events[event.get_signature()] = now
        
        logger.info(f"Disk I/O anomaly detected: {max_io:.1f} MB/s")
        return event
    
    def _cleanup_event_cache(self, now: float) -> None:
        """Remove old event signatures from cache."""
        expired = [
            sig for sig, timestamp in self.recent_events.items()
            if now - timestamp > self.cooldown
        ]
        for sig in expired:
            del self.recent_events[sig]
