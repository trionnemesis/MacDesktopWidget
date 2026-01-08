"""
Battery and temperature monitoring module using psutil.
"""
import psutil
import platform
import subprocess
import logging
from typing import Optional

from .data_structures import BatteryData, TemperatureData

logger = logging.getLogger(__name__)


class BatteryMonitor:
    """Monitor battery health and temperature information."""

    def __init__(self) -> None:
        """Initialize battery monitor."""
        self.is_macos = platform.system() == 'Darwin'
        self.sensors_available = hasattr(psutil, 'sensors_temperatures')

        logger.info(f"Battery Monitor initialized (macOS: {self.is_macos})")

    def get_battery_data(self) -> Optional[BatteryData]:
        """
        Collect current battery data.

        Returns:
            BatteryData with current battery metrics, or None if no battery.
        """
        try:
            battery = psutil.sensors_battery()

            if battery is None:
                # No battery available (desktop computer)
                return None

            # Get additional macOS-specific battery info
            health_percent = None
            cycle_count = None
            condition = None

            if self.is_macos:
                try:
                    health_percent, cycle_count, condition = self._get_macos_battery_health()
                except Exception as e:
                    logger.debug(f"Could not get macOS battery health: {e}")

            return BatteryData(
                percent=battery.percent,
                is_charging=battery.power_plugged,
                time_remaining_seconds=battery.secsleft if battery.secsleft > 0 else None,
                health_percent=health_percent,
                cycle_count=cycle_count,
                condition=condition
            )

        except Exception as e:
            logger.error(f"Error collecting battery data: {e}")
            return None

    def get_temperature_data(self) -> TemperatureData:
        """
        Collect current temperature data.

        Returns:
            TemperatureData with temperature metrics.
        """
        try:
            temps = {}

            if self.sensors_available:
                # Get temperature sensors
                temperatures = psutil.sensors_temperatures()

                if temperatures:
                    for name, entries in temperatures.items():
                        if entries:
                            # Take the first sensor or average if multiple
                            if len(entries) == 1:
                                temps[name] = entries[0].current
                            else:
                                temps[name] = sum(e.current for e in entries) / len(entries)

            # On macOS, try to get additional temperature info
            if self.is_macos:
                try:
                    macos_temps = self._get_macos_temperatures()
                    temps.update(macos_temps)
                except Exception as e:
                    logger.debug(f"Could not get macOS temperatures: {e}")

            # Calculate average and max
            avg_temp = None
            max_temp = None

            if temps:
                temp_values = list(temps.values())
                avg_temp = sum(temp_values) / len(temp_values)
                max_temp = max(temp_values)

            return TemperatureData(
                cpu_temp=temps.get('coretemp', temps.get('cpu', None)),
                gpu_temp=temps.get('gpu', None),
                avg_temp=avg_temp,
                max_temp=max_temp,
                all_sensors=temps
            )

        except Exception as e:
            logger.error(f"Error collecting temperature data: {e}")
            return TemperatureData(
                cpu_temp=None,
                gpu_temp=None,
                avg_temp=None,
                max_temp=None,
                all_sensors={}
            )

    def _get_macos_battery_health(self) -> tuple[Optional[int], Optional[int], Optional[str]]:
        """
        Get macOS-specific battery health information using system_profiler.

        Returns:
            Tuple of (health_percent, cycle_count, condition)
        """
        try:
            # Run system_profiler to get battery info
            result = subprocess.run(
                ['system_profiler', 'SPPowerDataType'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return None, None, None

            output = result.stdout

            # Parse the output
            health_percent = None
            cycle_count = None
            condition = None

            for line in output.split('\n'):
                line = line.strip()

                if 'Health Information:' in line or 'Condition:' in line:
                    # Look for condition in the next few lines
                    continue

                if 'Cycle Count:' in line:
                    try:
                        cycle_count = int(line.split(':')[1].strip())
                    except (ValueError, IndexError):
                        pass

                elif 'Condition:' in line or 'Battery Condition:' in line:
                    try:
                        condition = line.split(':')[1].strip()
                    except IndexError:
                        pass

                elif 'Maximum Capacity:' in line or 'State of Health:' in line:
                    try:
                        # Extract percentage
                        parts = line.split(':')[1].strip()
                        health_percent = int(parts.replace('%', '').strip())
                    except (ValueError, IndexError):
                        pass

            return health_percent, cycle_count, condition

        except subprocess.TimeoutExpired:
            logger.warning("Battery health check timed out")
            return None, None, None
        except Exception as e:
            logger.debug(f"Error getting macOS battery health: {e}")
            return None, None, None

    def _get_macos_temperatures(self) -> dict[str, float]:
        """
        Get macOS temperature information using powermetrics (requires sudo).

        Returns:
            Dictionary of temperature readings.
        """
        temps = {}

        try:
            # Try using osx-cpu-temp if available
            result = subprocess.run(
                ['which', 'osx-cpu-temp'],
                capture_output=True,
                timeout=2
            )

            if result.returncode == 0:
                result = subprocess.run(
                    ['osx-cpu-temp'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if result.returncode == 0:
                    try:
                        # Parse output like "61.0°C"
                        temp_str = result.stdout.strip().replace('°C', '').replace('°', '')
                        temps['cpu'] = float(temp_str)
                    except ValueError:
                        pass

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        except Exception as e:
            logger.debug(f"Error getting macOS temperature: {e}")

        return temps
