"""
System monitor orchestrator - coordinates all monitoring tasks.
"""
from PyQt6.QtCore import QThread, pyqtSignal
import time
import logging

from .cpu_monitor import CPUMonitor
from .memory_monitor import MemoryMonitor
from .disk_monitor import DiskMonitor
from .gpu_monitor import GPUMonitor
from .process_monitor import ProcessMonitor
from .network_monitor import NetworkMonitor
from .battery_monitor import BatteryMonitor
from .data_structures import SystemData

logger = logging.getLogger(__name__)


class SystemMonitor(QThread):
    """
    Main monitoring thread that coordinates all sub-monitors.
    Runs in background and emits signals with system data.
    """
    
    # Signal emitted with complete system data
    system_data_updated = pyqtSignal(SystemData)
    
    # Signal for errors
    error_occurred = pyqtSignal(str)
    
    def __init__(self, update_interval_ms: int = 1000, top_processes: int = 10):
        """
        Initialize system monitor.
        
        Args:
            update_interval_ms: Update interval in milliseconds.
            top_processes: Number of top processes to track.
        """
        super().__init__()
        
        self.update_interval_ms = update_interval_ms
        self.running = False
        
        # Initialize sub-monitors
        try:
            self.cpu_monitor = CPUMonitor()
            self.memory_monitor = MemoryMonitor()
            self.disk_monitor = DiskMonitor()
            self.gpu_monitor = GPUMonitor()
            self.process_monitor = ProcessMonitor(top_count=top_processes)
            self.network_monitor = NetworkMonitor()
            self.battery_monitor = BatteryMonitor()

            logger.info(f"System Monitor initialized (interval: {update_interval_ms}ms)")

        except Exception as e:
            logger.error(f"Error initializing monitors: {e}")
            raise
    
    def run(self) -> None:
        """Main monitoring loop (runs in thread)."""
        self.running = True
        logger.info("System Monitor started")
        
        target_interval = self.update_interval_ms / 1000.0  # Convert to seconds
        
        while self.running:
            try:
                start_time = time.time()
                
                # Collect all monitoring data
                system_data = self.collect_system_data()
                
                # Emit signal with data
                self.system_data_updated.emit(system_data)
                
                # Calculate sleep time to maintain interval
                elapsed = time.time() - start_time
                sleep_time = max(0, target_interval - elapsed)
                
                # Log if collection took too long
                if elapsed > target_interval:
                    logger.warning(f"Monitoring took {elapsed*1000:.1f}ms (target: {target_interval*1000:.1f}ms)")
                
                # Sleep in small increments to allow faster shutdown
                remaining = sleep_time
                while remaining > 0 and self.running:
                    time.sleep(min(0.1, remaining))
                    remaining -= 0.1
            
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                self.error_occurred.emit(str(e))
                time.sleep(1)  # Wait before retrying
        
        logger.info("System Monitor stopped")
   
    def collect_system_data(self) -> SystemData:
        """
        Collect data from all monitors.
        
        Returns:
            SystemData with current system metrics.
        """
        timestamp = time.time()
        
        try:
            # Collect from each monitor
            cpu_data = self.cpu_monitor.get_cpu_data()
            memory_data = self.memory_monitor.get_memory_data()
            disk_data = self.disk_monitor.get_disk_data()
            gpu_data = self.gpu_monitor.get_gpu_data()
            process_data = self.process_monitor.get_process_data()
            network_data = self.network_monitor.get_network_data()
            battery_data = self.battery_monitor.get_battery_data()
            temperature_data = self.battery_monitor.get_temperature_data()

            return SystemData(
                timestamp=timestamp,
                cpu=cpu_data,
                memory=memory_data,
                disk=disk_data,
                gpu=gpu_data,
                processes=process_data,
                network=network_data,
                battery=battery_data,
                temperature=temperature_data
            )
        
        except Exception as e:
            logger.error(f"Error collecting system data: {e}")
            raise
    
    def stop(self) -> None:
        """Stop the monitoring thread."""
        logger.info("Stopping System Monitor...")
        self.running = False
        
    def set_update_interval(self, interval_ms: int) -> None:
        """
        Change the update interval.
        
        Args:
            interval_ms: New interval in milliseconds.
        """
        if interval_ms < 100:
            logger.warning(f"Update interval {interval_ms}ms too low, setting to 100ms")
            interval_ms = 100
        
        self.update_interval_ms = interval_ms
        logger.info(f"Update interval changed to {interval_ms}ms")
