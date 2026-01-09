"""
Mock test data for testing purposes.
"""
import time
from src.python.monitoring.data_structures import (
    CPUData, MemoryData, DiskData, GPUData, ProcessData,
    ProcessInfo, PartitionInfo, SystemData,
    NetworkData, NetworkIOCounters, ProcessNetworkInfo,
    BatteryData, TemperatureData
)


def create_mock_cpu_data(total_percent: float = 45.0) -> CPUData:
    """Create mock CPU data."""
    return CPUData(
        total_percent=total_percent,
        per_core_percent=[50.0, 40.0, 45.0, 42.0],
        frequency_mhz=2400.0
    )


def create_mock_memory_data(percent: float = 65.0) -> MemoryData:
    """Create mock memory data."""
    total = 16 * 1024**3  # 16GB
    used = int(total * percent / 100)
    
    return MemoryData(
        total_bytes=total,
        used_bytes=used,
        available_bytes=total - used,
        percent=percent,
        swap_used_bytes=512 * 1024**2,  # 512MB
        swap_total_bytes=2 * 1024**3  # 2GB
    )


def create_mock_disk_data(read_mb: float = 50.0, write_mb: float = 30.0) -> DiskData:
    """Create mock disk data."""
    return DiskData(
        read_bytes_per_sec=read_mb * 1024**2,
        write_bytes_per_sec=write_mb * 1024**2,
        partitions={
            "/": PartitionInfo(
                mountpoint="/",
                fstype="apfs",
                total_bytes=500 * 1024**3,
                used_bytes=300 * 1024**3,
                free_bytes=200 * 1024**3,
                percent=60.0
            )
        }
    )


def create_mock_gpu_data(available: bool = True, utilization: float = 35.0) -> GPUData:
    """Create mock GPU data."""
    if not available:
        return GPUData(available=False, error_message="GPU monitoring unavailable")
    
    return GPUData(
        utilization_percent=utilization,
        memory_used_bytes=2 * 1024**3,  # 2GB
        memory_total_bytes=8 * 1024**3,  # 8GB
        available=True
    )


def create_mock_process_data() -> ProcessData:
    """Create mock process data."""
    processes = [
        ProcessInfo(pid=1234, name="Chrome", cpu_percent=25.0, memory_percent=15.0, status="running", memory_bytes=2400*1024**2),
        ProcessInfo(pid=5678, name="Safari", cpu_percent=10.0, memory_percent=8.0, status="running", memory_bytes=1280*1024**2),
        ProcessInfo(pid=9012, name="Python", cpu_percent=8.0, memory_percent=5.0, status="running", memory_bytes=800*1024**2),
        ProcessInfo(pid=3456, name="Docker", cpu_percent=5.0, memory_percent=12.0, status="running", memory_bytes=1920*1024**2),
        ProcessInfo(pid=7890, name="VSCode", cpu_percent=4.0, memory_percent=6.0, status="running", memory_bytes=960*1024**2),
    ]
    
    return ProcessData(
        top_by_cpu=sorted(processes, key=lambda p: p.cpu_percent, reverse=True),
        top_by_memory=sorted(processes, key=lambda p: p.memory_percent, reverse=True),
        total_processes=150
    )


def create_mock_network_data(upload_mb: float = 5.0, download_mb: float = 10.0) -> NetworkData:
    """Create mock network data."""
    return NetworkData(
        upload_bytes_per_sec=upload_mb * 1024**2,
        download_bytes_per_sec=download_mb * 1024**2,
        io_counters=NetworkIOCounters(
            bytes_sent=1024**3,  # 1GB
            bytes_recv=2 * 1024**3,  # 2GB
            packets_sent=1000000,
            packets_recv=1500000,
            errin=10,
            errout=5,
            dropin=2,
            dropout=1
        ),
        top_processes=[
            ProcessNetworkInfo(pid=1234, name="Chrome", upload_bytes_per_sec=3*1024**2, download_bytes_per_sec=8*1024**2, connections_count=50),
            ProcessNetworkInfo(pid=5678, name="Dropbox", upload_bytes_per_sec=2*1024**2, download_bytes_per_sec=1*1024**2, connections_count=5),
        ]
    )


def create_mock_battery_data(percent: float = 75.0, is_charging: bool = False, health: int = 85) -> BatteryData:
    """Create mock battery data."""
    return BatteryData(
        percent=percent,
        is_charging=is_charging,
        time_remaining_seconds=7200 if not is_charging else None,  # 2 hours
        health_percent=health,
        cycle_count=450,
        condition="Normal"
    )


def create_mock_temperature_data(cpu_temp: float = 65.0, gpu_temp: float = 60.0) -> TemperatureData:
    """Create mock temperature data."""
    return TemperatureData(
        cpu_temp=cpu_temp,
        gpu_temp=gpu_temp,
        avg_temp=(cpu_temp + gpu_temp) / 2,
        max_temp=max(cpu_temp, gpu_temp),
        all_sensors={"cpu": cpu_temp, "gpu": gpu_temp, "system": 58.0}
    )


def create_mock_system_data(
    cpu_percent: float = 45.0,
    memory_percent: float = 65.0,
    disk_read_mb: float = 50.0,
    disk_write_mb: float = 30.0,
    network_upload_mb: float = 5.0,
    network_download_mb: float = 10.0,
    battery_percent: float = 75.0,
    battery_health: int = 85,
    cpu_temp: float = 65.0
) -> SystemData:
    """Create complete mock system data."""
    return SystemData(
        timestamp=time.time(),
        cpu=create_mock_cpu_data(cpu_percent),
        memory=create_mock_memory_data(memory_percent),
        disk=create_mock_disk_data(disk_read_mb, disk_write_mb),
        gpu=create_mock_gpu_data(),
        processes=create_mock_process_data(),
        network=create_mock_network_data(network_upload_mb, network_download_mb),
        battery=create_mock_battery_data(battery_percent, False, battery_health),
        temperature=create_mock_temperature_data(cpu_temp)
    )


# Predefined scenarios for testing
SCENARIO_NORMAL = create_mock_system_data(cpu_percent=45.0, memory_percent=65.0)
SCENARIO_HIGH_CPU = create_mock_system_data(cpu_percent=92.0, memory_percent=65.0)
SCENARIO_HIGH_MEMORY = create_mock_system_data(cpu_percent=45.0, memory_percent=94.0)
SCENARIO_HIGH_DISK_IO = create_mock_system_data(cpu_percent=45.0, memory_percent=65.0, disk_read_mb=250.0, disk_write_mb=300.0)
SCENARIO_HIGH_NETWORK = create_mock_system_data(network_upload_mb=60.0, network_download_mb=80.0)
SCENARIO_LOW_BATTERY = create_mock_system_data(battery_percent=15.0)
SCENARIO_POOR_BATTERY_HEALTH = create_mock_system_data(battery_health=65)
SCENARIO_HIGH_TEMPERATURE = create_mock_system_data(cpu_temp=88.0)
