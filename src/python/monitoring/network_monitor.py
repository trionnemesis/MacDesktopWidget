"""
Network I/O monitoring module using psutil.
"""
import psutil
import time
import logging
from typing import Dict, Optional

from .data_structures import NetworkData, NetworkIOCounters, ProcessNetworkInfo

logger = logging.getLogger(__name__)


class NetworkMonitor:
    """Monitor network I/O statistics and per-process network usage."""

    def __init__(self) -> None:
        """Initialize network monitor."""
        self.last_io_counters: Optional[psutil._common.snetio] = None
        self.last_check_time: Optional[float] = None
        self.last_process_io: Dict[int, tuple] = {}  # pid -> (bytes_sent, bytes_recv, timestamp)

        logger.info("Network Monitor initialized")

    def get_network_data(self) -> NetworkData:
        """
        Collect current network data.

        Returns:
            NetworkData with current network metrics.
        """
        try:
            now = time.time()

            # Get system-wide network I/O
            io_counters = psutil.net_io_counters()

            # Calculate rates
            upload_bytes_per_sec = 0.0
            download_bytes_per_sec = 0.0

            if self.last_io_counters and self.last_check_time:
                time_delta = now - self.last_check_time
                if time_delta > 0:
                    upload_bytes_per_sec = (
                        io_counters.bytes_sent - self.last_io_counters.bytes_sent
                    ) / time_delta
                    download_bytes_per_sec = (
                        io_counters.bytes_recv - self.last_io_counters.bytes_recv
                    ) / time_delta

            # Store current values for next calculation
            self.last_io_counters = io_counters
            self.last_check_time = now

            # Create IO counters object
            io_data = NetworkIOCounters(
                bytes_sent=io_counters.bytes_sent,
                bytes_recv=io_counters.bytes_recv,
                packets_sent=io_counters.packets_sent,
                packets_recv=io_counters.packets_recv,
                errin=io_counters.errin,
                errout=io_counters.errout,
                dropin=io_counters.dropin,
                dropout=io_counters.dropout
            )

            # Get top network processes
            top_processes = self._get_top_network_processes()

            return NetworkData(
                upload_bytes_per_sec=max(0, upload_bytes_per_sec),
                download_bytes_per_sec=max(0, download_bytes_per_sec),
                io_counters=io_data,
                top_processes=top_processes
            )

        except Exception as e:
            logger.error(f"Error collecting network data: {e}")
            # Return empty data on error
            return NetworkData(
                upload_bytes_per_sec=0.0,
                download_bytes_per_sec=0.0,
                io_counters=NetworkIOCounters(
                    bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0,
                    errin=0, errout=0, dropin=0, dropout=0
                ),
                top_processes=[]
            )

    def _get_top_network_processes(self, top_count: int = 5) -> list[ProcessNetworkInfo]:
        """
        Get top processes by network usage.

        Args:
            top_count: Number of top processes to return.

        Returns:
            List of ProcessNetworkInfo sorted by total network usage.
        """
        process_network = []
        now = time.time()

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pid = proc.info['pid']
                name = proc.info['name'] or 'Unknown'

                # Get network connections for this process
                try:
                    connections = proc.net_io_counters()
                    if connections is None:
                        continue

                    bytes_sent = connections.bytes_sent
                    bytes_recv = connections.bytes_recv

                except (psutil.AccessDenied, AttributeError):
                    # net_io_counters() not available on all platforms
                    # Fall back to tracking connections
                    continue

                # Calculate rate if we have previous data
                upload_rate = 0.0
                download_rate = 0.0

                if pid in self.last_process_io:
                    last_sent, last_recv, last_time = self.last_process_io[pid]
                    time_delta = now - last_time
                    if time_delta > 0:
                        upload_rate = (bytes_sent - last_sent) / time_delta
                        download_rate = (bytes_recv - last_recv) / time_delta

                # Store current values
                self.last_process_io[pid] = (bytes_sent, bytes_recv, now)

                # Only include processes with active network usage
                if upload_rate > 0 or download_rate > 0:
                    process_network.append(ProcessNetworkInfo(
                        pid=pid,
                        name=name,
                        upload_bytes_per_sec=max(0, upload_rate),
                        download_bytes_per_sec=max(0, download_rate),
                        connections_count=len(proc.net_connections())
                    ))

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logger.debug(f"Error getting network info for process: {e}")
                continue

        # Clean up old process data
        self._cleanup_old_process_data(now)

        # Sort by total bandwidth (upload + download) and return top N
        process_network.sort(
            key=lambda p: p.upload_bytes_per_sec + p.download_bytes_per_sec,
            reverse=True
        )

        return process_network[:top_count]

    def _cleanup_old_process_data(self, now: float, max_age: float = 60.0) -> None:
        """
        Remove data for processes that haven't been seen recently.

        Args:
            now: Current timestamp.
            max_age: Maximum age in seconds.
        """
        old_pids = [
            pid for pid, (_, _, timestamp) in self.last_process_io.items()
            if now - timestamp > max_age
        ]
        for pid in old_pids:
            del self.last_process_io[pid]
