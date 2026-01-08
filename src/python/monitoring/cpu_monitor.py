"""
CPU monitoring module using psutil.
"""
import psutil
from typing import Optional, List
import logging

from .data_structures import CPUData

logger = logging.getLogger(__name__)


class CPUMonitor:
    """Monitor CPU usage and statistics."""
    
    def __init__(self) -> None:
        """Initialize CPU monitor."""
        # Initialize psutil CPU percent (first call returns 0)
        psutil.cpu_percent(interval=None, percpu=True)
        logger.info("CPU Monitor initialized")
    
    def get_cpu_data(self) -> CPUData:
        """
        Collect current CPU data.
        
        Returns:
            CPUData with current CPU metrics.
        """
        try:
            # Get overall CPU percentage (non-blocking)
            total_percent = psutil.cpu_percent(interval=None)
            
            # Get per-core percentages
            per_core = psutil.cpu_percent(interval=None, percpu=True)
            
            # Get CPU frequency (if available)
            freq = None
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    freq = cpu_freq.current
            except (AttributeError, NotImplementedError):
                # CPU frequency not available on all platforms
                pass
            
            return CPUData(
                total_percent=total_percent,
                per_core_percent=list(per_core),
                frequency_mhz=freq
            )
        
        except Exception as e:
            logger.error(f"Error collecting CPU data: {e}")
            # Return minimal valid data on error
            return CPUData(
                total_percent=0.0,
                per_core_percent=[0.0],
                frequency_mhz=None
            )
    
    def get_cpu_count(self) -> int:
        """Get number of CPU cores."""
        return psutil.cpu_count(logical=True) or 1
    
    def get_physical_cpu_count(self) -> int:
        """Get number of physical CPU cores."""
        return psutil.cpu_count(logical=False) or 1
