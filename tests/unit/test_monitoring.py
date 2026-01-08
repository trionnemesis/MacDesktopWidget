"""
Basic unit tests for monitoring components.
"""
import pytest
from unittest.mock import Mock, patch
import psutil

from src.python.monitoring.cpu_monitor import CPUMonitor
from src.python.monitoring.memory_monitor import MemoryMonitor
from src.python.monitoring.process_monitor import ProcessMonitor
from src.python.monitoring.anomaly_detector import AnomalyDetector, AnomalyType
from tests.fixtures.mock_data import create_mock_system_data


class TestCPUMonitor:
    """Test CPU monitoring."""
    
    def test_cpu_monitor_initialization(self):
        """Test CPU monitor can be initialized."""
        monitor = CPUMonitor()
        assert monitor is not None
    
    @patch('psutil.cpu_percent')
    def test_get_cpu_data(self, mock_cpu_percent):
        """Test getting CPU data."""
        mock_cpu_percent.return_value = 45.0
        
        monitor = CPUMonitor()
        data = monitor.get_cpu_data()
        
        assert data.total_percent >= 0
        assert data.total_percent <= 100
        assert len(data.per_core_percent) > 0


class TestMemoryMonitor:
    """Test memory monitoring."""
    
    def test_memory_monitor_initialization(self):
        """Test memory monitor can be initialized."""
        monitor = MemoryMonitor()
        assert monitor is not None
    
    def test_get_memory_data(self):
        """Test getting memory data."""
        monitor = MemoryMonitor()
        data = monitor.get_memory_data()
        
        assert data.total_bytes > 0
        assert data.percent >= 0
        assert data.percent <= 100
        assert data.used_gb > 0


class TestProcessMonitor:
    """Test process monitoring."""
    
    def test_process_monitor_initialization(self):
        """Test process monitor can be initialized."""
        monitor = ProcessMonitor(top_count=10)
        assert monitor is not None
        assert monitor.top_count == 10
    
    def test_get_process_data(self):
        """Test getting process data."""
        monitor = ProcessMonitor(top_count=5)
        data = monitor.get_process_data()
        
        assert len(data.top_by_cpu) <= 5
        assert len(data.top_by_memory) <= 5
        assert data.total_processes >= 0


class TestAnomalyDetector:
    """Test anomaly detection."""
    
    def test_anomaly_detector_initialization(self):
        """Test anomaly detector can be initialized."""
        detector = AnomalyDetector()
        assert detector is not None
        assert detector.cpu_threshold == 80.0
        assert detector.memory_threshold == 90.0
    
    def test_no_anomaly_on_normal_data(self):
        """Test that normal data doesn't trigger anomalies."""
        detector = AnomalyDetector()
        system_data = create_mock_system_data(cpu_percent=45.0, memory_percent=65.0)
        
        events = detector.check_system_data(system_data)
        assert len(events) == 0
    
    def test_cpu_anomaly_detection(self):
        """Test CPU anomaly detection."""
        detector = AnomalyDetector(cpu_duration=0.1)  # Short duration for testing
        
        # Create high CPU data
        system_data = create_mock_system_data(cpu_percent=92.0)
        
        # First check - should not trigger (not sustained)
        events = detector.check_system_data(system_data)
        assert len(events) == 0
        
        # Wait and check again
        import time
        time.sleep(0.15)
        
        events = detector.check_system_data(system_data)
        # Should trigger now
        assert len(events) > 0
        assert events[0].type == AnomalyType.CPU
    
    def test_memory_anomaly_detection(self):
        """Test memory anomaly detection."""
        detector = AnomalyDetector(memory_duration=0.1)
        
        system_data = create_mock_system_data(memory_percent=94.0)
        
        # Not triggered immediately
        events = detector.check_system_data(system_data)
        assert len(events) == 0
        
        # Wait for duration
        import time
        time.sleep(0.15)
        
        events = detector.check_system_data(system_data)
        assert len(events) > 0
        assert events[0].type == AnomalyType.MEMORY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
