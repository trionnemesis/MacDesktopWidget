"""
Unit tests for extended monitoring components (Network, Battery, Temperature).
"""
import pytest
from unittest.mock import Mock, patch
import time

from src.python.monitoring.network_monitor import NetworkMonitor
from src.python.monitoring.battery_monitor import BatteryMonitor
from src.python.monitoring.anomaly_detector import AnomalyDetector, AnomalyType
from tests.fixtures.mock_data import (
    create_mock_system_data,
    create_mock_network_data,
    create_mock_battery_data,
    create_mock_temperature_data,
    SCENARIO_HIGH_NETWORK,
    SCENARIO_LOW_BATTERY,
    SCENARIO_POOR_BATTERY_HEALTH,
    SCENARIO_HIGH_TEMPERATURE
)


class TestNetworkMonitor:
    """Test network monitoring."""

    def test_network_monitor_initialization(self):
        """Test network monitor can be initialized."""
        monitor = NetworkMonitor()
        assert monitor is not None
        assert monitor.last_io_counters is None

    @patch('psutil.net_io_counters')
    def test_get_network_data(self, mock_net_io):
        """Test getting network data."""
        # Mock psutil data
        mock_counter = Mock()
        mock_counter.bytes_sent = 1024**3
        mock_counter.bytes_recv = 2 * 1024**3
        mock_counter.packets_sent = 1000000
        mock_counter.packets_recv = 1500000
        mock_counter.errin = 10
        mock_counter.errout = 5
        mock_counter.dropin = 2
        mock_counter.dropout = 1
        mock_net_io.return_value = mock_counter

        monitor = NetworkMonitor()
        data = monitor.get_network_data()

        assert data is not None
        assert data.upload_bytes_per_sec >= 0
        assert data.download_bytes_per_sec >= 0
        assert data.io_counters is not None

    def test_network_data_properties(self):
        """Test network data property calculations."""
        data = create_mock_network_data(upload_mb=10.0, download_mb=20.0)

        assert data.upload_mb_per_sec == 10.0
        assert data.download_mb_per_sec == 20.0
        assert data.total_mb_per_sec == 30.0


class TestBatteryMonitor:
    """Test battery and temperature monitoring."""

    def test_battery_monitor_initialization(self):
        """Test battery monitor can be initialized."""
        monitor = BatteryMonitor()
        assert monitor is not None

    @patch('psutil.sensors_battery')
    def test_get_battery_data_no_battery(self, mock_battery):
        """Test getting battery data when no battery is present."""
        mock_battery.return_value = None

        monitor = BatteryMonitor()
        data = monitor.get_battery_data()

        assert data is None

    @patch('psutil.sensors_battery')
    def test_get_battery_data_with_battery(self, mock_battery):
        """Test getting battery data with battery present."""
        mock_bat = Mock()
        mock_bat.percent = 80.0
        mock_bat.power_plugged = False
        mock_bat.secsleft = 7200  # 2 hours
        mock_battery.return_value = mock_bat

        monitor = BatteryMonitor()
        data = monitor.get_battery_data()

        assert data is not None
        assert data.percent == 80.0
        assert data.is_charging is False
        assert data.time_remaining_seconds == 7200

    def test_battery_data_properties(self):
        """Test battery data property calculations."""
        data = create_mock_battery_data(percent=50.0, is_charging=False)

        assert data.time_remaining_hours == 2.0  # 7200 seconds = 2 hours

    def test_get_temperature_data(self):
        """Test getting temperature data."""
        monitor = BatteryMonitor()
        data = monitor.get_temperature_data()

        # Temperature data should always return (may be empty)
        assert data is not None

    def test_temperature_data_calculations(self):
        """Test temperature data calculations."""
        data = create_mock_temperature_data(cpu_temp=70.0, gpu_temp=65.0)

        assert data.avg_temp == 67.5
        assert data.max_temp == 70.0
        assert "cpu" in data.all_sensors
        assert "gpu" in data.all_sensors


class TestExtendedAnomalyDetection:
    """Test anomaly detection for new monitoring types."""

    def test_network_anomaly_detection(self):
        """Test network I/O anomaly detection."""
        detector = AnomalyDetector(
            network_io_threshold_mb=50.0,
            network_duration=0.1
        )

        # High network traffic
        system_data = create_mock_system_data(
            network_upload_mb=60.0,
            network_download_mb=80.0
        )

        # First check - not triggered yet
        events = detector.check_system_data(system_data)
        assert len(events) == 0

        # Wait for duration
        time.sleep(0.15)

        # Should trigger now
        events = detector.check_system_data(system_data)
        network_events = [e for e in events if e.type == AnomalyType.NETWORK_IO]
        assert len(network_events) > 0

    def test_battery_low_anomaly_detection(self):
        """Test battery low anomaly detection."""
        detector = AnomalyDetector(
            battery_low_threshold=20.0,
            battery_duration=0.1
        )

        # Low battery
        system_data = create_mock_system_data(battery_percent=15.0)

        # First check
        events = detector.check_system_data(system_data)
        assert len(events) == 0

        # Wait for duration
        time.sleep(0.15)

        # Should trigger
        events = detector.check_system_data(system_data)
        battery_events = [e for e in events if e.type == AnomalyType.BATTERY_LOW]
        assert len(battery_events) > 0
        assert battery_events[0].metrics["battery_percent"] == 15.0

    def test_battery_health_anomaly_detection(self):
        """Test battery health anomaly detection."""
        detector = AnomalyDetector(
            battery_health_threshold=80,
            battery_duration=0.1
        )

        # Poor battery health
        system_data = create_mock_system_data(battery_health=65)

        # First check
        events = detector.check_system_data(system_data)
        assert len(events) == 0

        # Wait for duration
        time.sleep(0.15)

        # Should trigger
        events = detector.check_system_data(system_data)
        health_events = [e for e in events if e.type == AnomalyType.BATTERY_HEALTH]
        assert len(health_events) > 0

    def test_temperature_anomaly_detection(self):
        """Test high temperature anomaly detection."""
        detector = AnomalyDetector(
            temperature_threshold=80.0,
            temperature_duration=0.1
        )

        # High temperature
        system_data = create_mock_system_data(cpu_temp=88.0)

        # First check
        events = detector.check_system_data(system_data)
        assert len(events) == 0

        # Wait for duration
        time.sleep(0.15)

        # Should trigger
        events = detector.check_system_data(system_data)
        temp_events = [e for e in events if e.type == AnomalyType.HIGH_TEMPERATURE]
        assert len(temp_events) > 0
        assert temp_events[0].metrics["max_temp"] == 88.0

    def test_no_anomaly_with_normal_extended_data(self):
        """Test that normal data doesn't trigger new anomaly types."""
        detector = AnomalyDetector()
        system_data = create_mock_system_data(
            network_upload_mb=10.0,
            battery_percent=75.0,
            battery_health=85,
            cpu_temp=65.0
        )

        events = detector.check_system_data(system_data)

        # Should not have network, battery, or temperature anomalies
        network_events = [e for e in events if e.type == AnomalyType.NETWORK_IO]
        battery_events = [e for e in events if e.type in [AnomalyType.BATTERY_LOW, AnomalyType.BATTERY_HEALTH]]
        temp_events = [e for e in events if e.type == AnomalyType.HIGH_TEMPERATURE]

        assert len(network_events) == 0
        assert len(battery_events) == 0
        assert len(temp_events) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
