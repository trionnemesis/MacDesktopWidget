"""
Memory monitoring module using psutil.
"""
import psutil
import logging

from .data_structures import MemoryData

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """Monitor memory (RAM) usage and statistics."""
    
    def __init__(self) -> None:
        """Initialize memory monitor."""
        logger.info("Memory Monitor initialized")
    
    def get_memory_data(self) -> MemoryData:
        """
        Collect current memory data.
        
        Returns:
            MemoryData with current memory metrics.
        """
        try:
            # Get virtual memory statistics
            vm = psutil.virtual_memory()
            
            # Get swap memory statistics
            swap = psutil.swap_memory()
            
            return MemoryData(
                total_bytes=vm.total,
                used_bytes=vm.used,
                available_bytes=vm.available,
                percent=vm.percent,
                swap_used_bytes=swap.used,
                swap_total_bytes=swap.total
            )
        
        except Exception as e:
            logger.error(f"Error collecting memory data: {e}")
            # Return minimal valid data on error
            return MemoryData(
                total_bytes=1024 ** 3,  # 1GB placeholder
                used_bytes=0,
                available_bytes=1024 ** 3,
                percent=0.0,
                swap_used_bytes=0,
                swap_total_bytes=0
            )
