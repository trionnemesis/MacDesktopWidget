"""
GPU monitoring module for macOS.
Falls back gracefully if GPU monitoring is unavailable.
"""
import subprocess
import logging
import platform
from typing import Optional

from .data_structures import GPUData

logger = logging.getLogger(__name__)


class GPUMonitor:
    """Monitor GPU usage (macOS-specific with fallback)."""
    
    def __init__(self) -> None:
        """Initialize GPU monitor."""
        self.is_macos = platform.system() == "Darwin"
        self.macmon_available = self._check_macmon()
        
        if not self.is_macos:
            logger.info("GPU monitoring only supported on macOS")
        elif self.macmon_available:
            logger.info("GPU Monitor initialized with macmon")
        else:
            logger.info("GPU Monitor initialized with fallback (macmon not available)")
    
    def _check_macmon(self) -> bool:
        """Check if macmon library is available."""
        try:
            import macmon  # type: ignore
            return True
        except ImportError:
            return False
    
    def get_gpu_data(self) -> GPUData:
        """
        Collect current GPU data.
        
        Returns:
            GPUData with current GPU metrics or unavailable status.
        """
        if not self.is_macos:
            return GPUData(
                available=False,
                error_message="GPU monitoring only supported on macOS"
            )
        
        if self.macmon_available:
            return self._get_gpu_data_macmon()
        else:
            return self._get_gpu_data_fallback()
    
    def _get_gpu_data_macmon(self) -> GPUData:
        """
        Get GPU data using macmon library.
        
        Returns:
            GPUData with GPU metrics.
        """
        try:
            import macmon  # type: ignore
            
            # Get GPU metrics from macmon
            # Note: Actual macmon API may differ - this is a placeholder
            # Adjust based on actual macmon documentation
            metrics = macmon.get_gpu_metrics()
            
            return GPUData(
                utilization_percent=metrics.get('utilization', 0.0),
                memory_used_bytes=metrics.get('memory_used', 0),
                memory_total_bytes=metrics.get('memory_total', 0),
                available=True
            )
        
        except Exception as e:
            logger.error(f"Error getting GPU data from macmon: {e}")
            return GPUData(
                available=False,
                error_message=f"macmon error: {str(e)}"
            )
    
    def _get_gpu_data_fallback(self) -> GPUData:
        """
        Fallback GPU data using system_profiler.
        Limited information available.
        
        Returns:
            GPUData with basic GPU info or unavailable status.
        """
        try:
            # Use system_profiler to get basic GPU info
            result = subprocess.run(
                ['system_profiler', 'SPDisplaysDataType'],
                capture_output=True,
                text=True,
                timeout=2.0
            )
            
            if result.returncode == 0:
                # Successfully got GPU info, but no real-time metrics available
                # Just indicate GPU is present
                return GPUData(
                    available=True,
                    utilization_percent=None,
                    memory_used_bytes=None,
                    memory_total_bytes=None,
                    error_message="Real-time GPU metrics unavailable (install macmon for full support)"
                )
            else:
                return GPUData(
                    available=False,
                    error_message="Could not detect GPU"
                )
        
        except subprocess.TimeoutExpired:
            logger.warning("system_profiler timeout")
            return GPUData(
                available=False,
                error_message="GPU detection timeout"
            )
        
        except Exception as e:
            logger.error(f"Error in fallback GPU detection: {e}")
            return GPUData(
                available=False,
                error_message=f"GPU detection failed: {str(e)}"
            )
