"""
Disk I/O monitoring module using psutil.
"""
import psutil
import time
from typing import Optional
import logging

from .data_structures import DiskData, PartitionInfo

logger = logging.getLogger(__name__)


class DiskMonitor:
    """Monitor disk I/O and usage statistics."""
    
    def __init__(self) -> None:
        """Initialize disk monitor."""
        self.prev_io_counters: Optional[psutil._common.sdiskio] = None
        self.prev_timestamp: Optional[float] = None
        
        # Initialize with first reading
        try:
            self.prev_io_counters = psutil.disk_io_counters()
            self.prev_timestamp = time.time()
        except Exception as e:
            logger.warning(f"Could not initialize disk I/O counters: {e}")
        
        logger.info("Disk Monitor initialized")
    
    def get_disk_data(self) -> DiskData:
        """
        Collect current disk data.
        
        Returns:
            DiskData with current disk I/O and usage metrics.
        """
        try:
            # Calculate I/O rates
            read_rate, write_rate = self._calc_io_rates()
            
            # Get partition usage
            partitions = self._get_partition_info()
            
            return DiskData(
                read_bytes_per_sec=read_rate,
                write_bytes_per_sec=write_rate,
                partitions=partitions
            )
        
        except Exception as e:
            logger.error(f"Error collecting disk data: {e}")
            # Return minimal valid data on error
            return DiskData(
                read_bytes_per_sec=0.0,
                write_bytes_per_sec=0.0,
                partitions={}
            )
    
    def _calc_io_rates(self) -> tuple[float, float]:
        """
        Calculate disk I/O rates in bytes per second.
        
        Returns:
            Tuple of (read_bytes_per_sec, write_bytes_per_sec).
        """
        try:
            current_io = psutil.disk_io_counters()
            current_time = time.time()
            
            if self.prev_io_counters is None or self.prev_timestamp is None:
                # First call - no rate yet
                self.prev_io_counters = current_io
                self.prev_timestamp = current_time
                return (0.0, 0.0)
            
            # Calculate time delta
            time_delta = current_time - self.prev_timestamp
            
            if time_delta == 0:
                return (0.0, 0.0)
            
            # Calculate byte deltas
            read_delta = current_io.read_bytes - self.prev_io_counters.read_bytes
            write_delta = current_io.write_bytes - self.prev_io_counters.write_bytes
            
            # Calculate rates
            read_rate = max(0, read_delta / time_delta)
            write_rate = max(0, write_delta / time_delta)
            
            # Update previous values
            self.prev_io_counters = current_io
            self.prev_timestamp = current_time
            
            return (read_rate, write_rate)
        
        except Exception as e:
            logger.error(f"Error calculating I/O rates: {e}")
            return (0.0, 0.0)
    
    def _get_partition_info(self) -> dict[str, PartitionInfo]:
        """
        Get information about all disk partitions.
        
        Returns:
            Dictionary mapping mountpoint to PartitionInfo.
        """
        partitions = {}
        
        try:
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    
                    partitions[part.mountpoint] = PartitionInfo(
                        mountpoint=part.mountpoint,
                        fstype=part.fstype,
                        total_bytes=usage.total,
                        used_bytes=usage.used,
                        free_bytes=usage.free,
                        percent=usage.percent
                    )
                except (PermissionError, OSError) as e:
                    # Skip partitions we can't access
                    logger.debug(f"Cannot access partition {part.mountpoint}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error getting partition info: {e}")
        
        return partitions
