"""
Main application class coordinating all components.
"""
import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSlot

from .config import get_config
from ..monitoring.system_monitor import SystemMonitor
from ..monitoring.anomaly_detector import AnomalyDetector
from ..ai.suggestion_engine import SuggestionEngine

logger = logging.getLogger(__name__)


class MacDesktopWidgetApp(QObject):
    """Main application coordinating all components."""
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Load configuration
        self.config = get_config()
        
        # Setup logging
        self._setup_logging()
        
        logger.info("=== MacDesktopWidget Starting ===")
        logger.info(f"Update Interval: {self.config.monitoring.update_interval_ms}ms")
        logger.info(f"AI Enabled: {self.config.ai.enable_ai}")
        
        # Initialize components
        self.system_monitor = None
        self.anomaly_detector = None
        self.suggestion_engine = None
        
        # UI (to be implemented)
        self.main_window = None
        
        self._init_components()
        self._connect_signals()
        self._init_ui()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.log_level)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('mac_desktop_widget.log')
            ]
        )
    
    def _init_components(self):
        """Initialize all application components."""
        logger.info("Initializing components...")
        
        # Initialize System Monitor
        self.system_monitor = SystemMonitor(
            update_interval_ms=self.config.monitoring.update_interval_ms,
            top_processes=self.config.monitoring.top_processes_count
        )
        
        # Initialize Anomaly Detector
        self.anomaly_detector = AnomalyDetector(
            cpu_threshold=self.config.monitoring.cpu_threshold,
            memory_threshold=self.config.monitoring.memory_threshold,
            process_threshold=self.config.monitoring.process_threshold,
            cpu_duration=3.0,
            memory_duration=5.0,
            process_duration=5.0,
            cooldown=60.0
        )
        
        # Initialize AI Suggestion Engine (if enabled)
        if self.config.ai.enable_ai:
            self.suggestion_engine = SuggestionEngine(
                api_key=self.config.ai.api_key,
                base_url=self.config.ai.base_url,
                model_name=self.config.ai.model_name,
                cache_duration=self.config.ai.suggestion_cache_duration_seconds,
                rate_limit_seconds=10,
                max_suggestion_length=self.config.ai.max_suggestion_length
            )
        else:
            logger.info("AI suggestions disabled")
        
        logger.info("Components initialized")
    
    def _init_ui(self):
        """Initialize UI window."""
        try:
            from ..ui.main_window import MainWindow
            
            self.main_window = MainWindow(self.config)
            logger.info("UI initialized")
        
        except Exception as e:
            logger.error(f"Error initializing UI: {e}")
            logger.info("Running in console mode")
            self.main_window = None
    
    def _connect_signals(self):
        """Connect signals between components."""
        logger.info("Connecting signals...")
        
        # System Monitor → Anomaly Detector
        self.system_monitor.system_data_updated.connect(
            self._on_system_data_updated
        )
        
        # System Monitor → Error handling
        self.system_monitor.error_occurred.connect(
            self._on_monitoring_error
        )
        
        # Suggestion Engine signals (if enabled)
        if self.suggestion_engine:
            self.suggestion_engine.suggestion_ready.connect(
                self._on_suggestion_ready
            )
            self.suggestion_engine.ai_status_changed.connect(
                self._on_ai_status_changed
            )
            self.suggestion_engine.error_occurred.connect(
                self._on_ai_error
            )
        
        # UI signals (if available)
        if self.main_window:
            # Connect system data to UI
            self.system_monitor.system_data_updated.connect(
                self.main_window.update_display
            )
            
            # Connect suggestions to UI
            if self.suggestion_engine:
                self.suggestion_engine.suggestion_ready.connect(
                    self.main_window.show_suggestion
                )
        
        logger.info("Signals connected")
    
    @pyqtSlot(object)
    def _on_system_data_updated(self, system_data):
        """
        Handle updated system data.
        
        Args:
            system_data: SystemData object.
        """
        # Update suggestion engine with latest data
        if self.suggestion_engine:
            self.suggestion_engine.update_system_data(system_data)
        
        # Check for anomalies
        anomaly_events = self.anomaly_detector.check_system_data(system_data)
        
        # Process any detected anomalies
        for event in anomaly_events:
            logger.info(f"Anomaly detected: {event.type.value} - {event.severity.value}")
            
            # Send to AI for suggestion (if enabled)
            if self.suggestion_engine:
                self.suggestion_engine.handle_anomaly(event)
    
    @pyqtSlot(str)
    def _on_monitoring_error(self, error_msg):
        """Handle monitoring errors."""
        logger.error(f"Monitoring error: {error_msg}")
    
    @pyqtSlot(object)
    def _on_suggestion_ready(self, suggestion):
        """
        Handle new AI suggestion.
        
        Args:
            suggestion: Suggestion object.
        """
        logger.info(f"AI Suggestion: {suggestion.text}")
        
        # Display in UI (to be implemented)
        # if self.main_window:
        #     self.main_window.show_suggestion(suggestion)
        
        # For now, just print to console
        print(f"\n🤖 AI 建議: {suggestion.text}\n")
    
    @pyqtSlot(bool)
    def _on_ai_status_changed(self, available):
        """Handle AI availability status changes."""
        if available:
            logger.info("✓ AI is available")
        else:
            logger.warning("✗ AI is NOT available - using fallback suggestions")
    
    @pyqtSlot(str)
    def _on_ai_error(self, error_msg):
        """Handle AI errors."""
        logger.error(f"AI error: {error_msg}")
    
    def start(self):
        """Start the application."""
        logger.info("Starting application components...")
        
        # Start monitoring thread
        self.system_monitor.start()
        logger.info("✓ System monitoring started")
        
        # Start suggestion engine thread (if enabled)
        if self.suggestion_engine:
            self.suggestion_engine.start()
            logger.info("✓ AI suggestion engine started")
        
        # Show UI
        if self.main_window:
            self.main_window.show()
            logger.info("✓ UI window shown")
        else:
            logger.info("Running in console mode (no UI)")
        
        logger.info("=== Application Running ===")
    
    def stop(self):
        """Stop the application."""
        logger.info("Stopping application...")
        
        # Stop monitoring
        if self.system_monitor:
            self.system_monitor.stop()
            self.system_monitor.wait(2000)  # Wait up to 2 seconds
            logger.info("✓ System monitoring stopped")
        
        # Stop suggestion engine
        if self.suggestion_engine:
            self.suggestion_engine.stop()
            self.suggestion_engine.wait(2000)
            logger.info("✓ AI suggestion engine stopped")
        
        logger.info("=== Application Stopped ===")


def create_app():
    """
    Create and return the application instance.
    
    Returns:
        Tuple of (QApplication, MacDesktopWidgetApp)
    """
    # Create Qt application
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("MacDesktopWidget")
    qt_app.setOrganizationName("MacDesktopWidget")
    
    # Create main app
    app = MacDesktopWidgetApp()
    
    # Handle quit signal
    qt_app.aboutToQuit.connect(app.stop)
    
    return qt_app, app
