"""
Process monitoring module using psutil.
"""
import psutil
import logging
from typing import List

from .data_structures import ProcessInfo, ProcessData

logger = logging.getLogger(__name__)


class ProcessMonitor:
    """Monitor running processes and their resource usage."""
    
    def __init__(self, top_count: int = 10) -> None:
        """
        Initialize process monitor.
        
        Args:
            top_count: Number of top processes to track.
        """
        self.top_count = top_count
        logger.info(f"Process Monitor initialized (top {top_count})")
    
    def get_process_data(self) -> ProcessData:
        """
        Collect current process data.
        
        Returns:
            ProcessData with top processes by CPU and Memory.
        """
        try:
            # Collect all accessible processes
            processes = self._collect_processes()
            
            # Sort by CPU
            top_by_cpu = sorted(
                processes,
                key=lambda p: p.cpu_percent,
                reverse=True
            )[:self.top_count]
            
            # Sort by Memory
            top_by_memory = sorted(
                processes,
                key=lambda p: p.memory_percent,
                reverse=True
            )[:self.top_count]
            
            return ProcessData(
                top_by_cpu=top_by_cpu,
                top_by_memory=top_by_memory,
                total_processes=len(processes)
            )
        
        except Exception as e:
            logger.error(f"Error collecting process data: {e}")
            # Return empty data on error
            return ProcessData(
                top_by_cpu=[],
                top_by_memory=[],
                total_processes=0
            )
    
    def _collect_processes(self) -> List[ProcessInfo]:
        """
        Collect information about all accessible processes.
        
        Returns:
            List of ProcessInfo objects.
        """
        processes = []
        
        # Iterate over all processes
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'memory_info']):
            try:
                # Get process info
                pinfo = proc.info
                
                # Extract memory bytes
                memory_bytes = 0
                if pinfo.get('memory_info'):
                    memory_bytes = pinfo['memory_info'].rss
                
                # Create ProcessInfo object
                proc_info = ProcessInfo(
                    pid=pinfo['pid'],
                    name=pinfo['name'] or 'Unknown',
                    cpu_percent=pinfo['cpu_percent'] or 0.0,
                    memory_percent=pinfo['memory_percent'] or 0.0,
                    status=pinfo.get('status', 'unknown'),
                    memory_bytes=memory_bytes
                )
                
                processes.append(proc_info)
            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes we can't access
                continue
            except Exception as e:
                logger.debug(f"Error processing process info: {e}")
                continue
        
        return processes
    
    def get_process_by_pid(self, pid: int) -> ProcessInfo:
        """
        Get detailed information about a specific process.
        
        Args:
            pid: Process ID.
        
        Returns:
            ProcessInfo for the specified process.
        
        Raises:
            psutil.NoSuchProcess: If process doesn't exist.
        """
        try:
            proc = psutil.Process(pid)
            
            return ProcessInfo(
                pid=pid,
                name=proc.name(),
                cpu_percent=proc.cpu_percent(interval=0.1),
                memory_percent=proc.memory_percent(),
                status=proc.status(),
                memory_bytes=proc.memory_info().rss
            )
        
        except psutil.NoSuchProcess:
            raise
        except Exception as e:
            logger.error(f"Error getting process {pid}: {e}")
            # Return minimal info
            return ProcessInfo(
                pid=pid,
                name="Unknown",
                cpu_percent=0.0,
                memory_percent=0.0,
                status="unknown",
                memory_bytes=0
            )
