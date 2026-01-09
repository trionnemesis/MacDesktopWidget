"""
Transparent frameless main window for MacDesktopWidget.
"""
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt, QPoint, pyqtSlot
from PyQt6.QtGui import QFont
import logging
import os

from ..monitoring.data_structures import SystemData
from ..ai.suggestion_engine import Suggestion

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Transparent frameless main window."""
    
    def __init__(self, config):
        """
        Initialize main window.
        
        Args:
            config: Application configuration.
        """
        super().__init__()
        
        self.config = config
        
        # Window dragging
        self.dragging = False
        self.drag_position = QPoint()
        
        # Setup window
        self._setup_window()
        self._setup_ui()
        self._load_stylesheet()
        
        logger.info("Main window initialized")
    
    def _setup_window(self):
        """Setup window properties."""
        # Set window flags for transparency and frameless
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Enable transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set minimum window size, allowing content to expand
        self.setMinimumWidth(self.config.ui.window_width)
        self.setMinimumHeight(self.config.ui.window_height)
        
        # Set title
        self.setWindowTitle("MacDesktopWidget")
    
    def _setup_ui(self):
        """Setup UI layout."""
        # Central widget
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Glass container
        glass_container = QWidget()
        glass_container.setObjectName("glassContainer")
        glass_container.setProperty("class", "GlassContainer")
        
        container_layout = QVBoxLayout(glass_container)
        container_layout.setContentsMargins(1, 1, 1, 1)
        container_layout.setSpacing(0)
        
        # Title bar
        title_bar = self._create_title_bar()
        container_layout.addWidget(title_bar)
        
        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)
        
        # Metrics grid (CPU, Memory, Disk, GPU)
        metrics_grid = self._create_metrics_grid()
        content_layout.addLayout(metrics_grid)
        
        # Process list placeholder
        process_label = QLabel("📊 Top Processes")
        process_label.setStyleSheet("font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.9);")
        content_layout.addWidget(process_label)
        
        self.process_text = QLabel("Loading...")
        self.process_text.setStyleSheet(
            "font-family: 'Menlo', 'Monaco', 'Consolas', 'Courier New', monospace; "
            "font-size: 10px; "
            "color: rgba(255,255,255,0.7);"
        )
        self.process_text.setWordWrap(True)
        content_layout.addWidget(self.process_text)
        
        # AI suggestion area
        self.suggestion_label = QLabel("")
        self.suggestion_label.setProperty("class", "AISuggestion")
        self.suggestion_label.setStyleSheet(
            "background: rgba(157, 78, 221, 0.3); "
            "border: 1px solid rgba(157, 78, 221, 0.5); "
            "border-radius: 8px; padding: 10px; "
            "font-size: 13px; color: #FFFFFF;"
        )
        self.suggestion_label.setWordWrap(True)
        self.suggestion_label.hide()
        content_layout.addWidget(self.suggestion_label)
        
        content_layout.addStretch()
        
        container_layout.addWidget(content_widget)
        main_layout.addWidget(glass_container)
    
    def _create_title_bar(self) -> QWidget:
        """Create custom title bar."""
        title_bar = QWidget()
        title_bar.setProperty("class", "TitleBar")
        title_bar.setFixedHeight(36)
        title_bar.setStyleSheet(
            "background: rgba(30, 30, 40, 0.5); "
            "border-bottom: 1px solid rgba(100, 200, 255, 0.2); "
            "border-top-left-radius: 16px; "
            "border-top-right-radius: 16px;"
        )
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Title
        title_label = QLabel("🖥️ Mac Desktop Widget")
        title_label.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 600;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Close button
        close_button = QPushButton("✕")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet(
            "background: rgba(255, 68, 68, 0.3); "
            "border: 1px solid rgba(255, 68, 68, 0.5); "
            "border-radius: 12px; "
            "color: #FFFFFF; font-size: 14px; font-weight: bold;"
        )
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        return title_bar
    
    def _create_metrics_grid(self) -> QGridLayout:
        """Create grid layout for metric widgets."""
        grid = QGridLayout()
        grid.setSpacing(12)
        
        # CPU widget
        self.cpu_widget = self._create_metric_widget("CPU", "0%")
        grid.addWidget(self.cpu_widget, 0, 0)
        
        # Memory widget
        self.memory_widget = self._create_metric_widget("Memory", "0 GB")
        grid.addWidget(self.memory_widget, 0, 1)
        
        # Disk widget
        self.disk_widget = self._create_metric_widget("Disk I/O", "0 MB/s")
        grid.addWidget(self.disk_widget, 1, 0)
        
        # GPU widget
        self.gpu_widget = self._create_metric_widget("GPU", "N/A")
        grid.addWidget(self.gpu_widget, 1, 1)
        
        return grid
    
    def _create_metric_widget(self, label: str, initial_value: str) -> QWidget:
        """Create a metric display widget."""
        widget = QWidget()
        widget.setProperty("class", "MetricWidget")
        widget.setStyleSheet(
            "background: rgba(40, 40, 50, 0.4); "
            "border: 1px solid rgba(100, 200, 255, 0.2); "
            "border-radius: 12px; padding: 12px;"
        )
        widget.setFixedHeight(80)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet(
            "color: rgba(255, 255, 255, 0.8); "
            "font-size: 11px; font-weight: 500;"
        )
        layout.addWidget(label_widget)
        
        # Value
        value_label = QLabel(initial_value)
        value_label.setObjectName(f"{label.lower()}_value")
        value_label.setStyleSheet(
            "color: #FFFFFF; font-size: 24px; font-weight: 700;"
        )
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        # Store reference to value label
        widget.value_label = value_label
        
        return widget
    
    def _load_stylesheet(self):
        """Load QSS stylesheet."""
        try:
            qss_path = os.path.join(
                os.path.dirname(__file__),
                'styles',
                'main.qss'
            )
            
            if os.path.exists(qss_path):
                with open(qss_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
                logger.info("Stylesheet loaded")
            else:
                logger.warning(f"Stylesheet not found: {qss_path}")
        
        except Exception as e:
            logger.error(f"Error loading stylesheet: {e}")
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
    
    @pyqtSlot(object)
    def update_display(self, system_data: SystemData):
        """
        Update display with new system data.
        
        Args:
            system_data: SystemData object.
        """
        try:
            # Update CPU
            cpu_text = f"{system_data.cpu.total_percent:.1f}%"
            self.cpu_widget.value_label.setText(cpu_text)
            
            # Update Memory
            mem_text = f"{system_data.memory.used_gb:.1f} GB"
            self.memory_widget.value_label.setText(mem_text)
            
            # Update Disk
            disk_read = system_data.disk.read_mb_per_sec
            disk_write = system_data.disk.write_mb_per_sec
            disk_text = f"↓{disk_read:.0f} ↑{disk_write:.0f}"
            self.disk_widget.value_label.setText(disk_text)
            
            # Update GPU
            if system_data.gpu and system_data.gpu.available:
                if system_data.gpu.utilization_percent is not None:
                    gpu_text = f"{system_data.gpu.utilization_percent:.1f}%"
                else:
                    gpu_text = "N/A"
            else:
                gpu_text = "N/A"
            self.gpu_widget.value_label.setText(gpu_text)
            
            # Update process list
            if system_data.processes.top_by_cpu:
                process_lines = []
                for i, proc in enumerate(system_data.processes.top_by_cpu[:5], 1):
                    process_lines.append(
                        f"{i}. {proc.name[:15]:15s} CPU:{proc.cpu_percent:5.1f}%"
                    )
                self.process_text.setText("\n".join(process_lines))
        
        except Exception as e:
            logger.error(f"Error updating display: {e}")
    
    @pyqtSlot(object)
    def show_suggestion(self, suggestion: Suggestion):
        """
        Show AI suggestion.
        
        Args:
            suggestion: Suggestion object.
        """
        try:
            # Show the suggestion
            self.suggestion_label.setText(f"🤖 {suggestion.text}")
            self.suggestion_label.show()
            
            # Color based on severity
            if suggestion.severity == "critical":
                bg_color = "rgba(255, 68, 68, 0.3)"
                border_color = "rgba(255, 68, 68, 0.5)"
            elif suggestion.severity == "warning":
                bg_color = "rgba(255, 152, 0, 0.3)"
                border_color = "rgba(255, 152, 0, 0.5)"
            else:
                bg_color = "rgba(157, 78, 221, 0.3)"
                border_color = "rgba(157, 78, 221, 0.5)"
            
            self.suggestion_label.setStyleSheet(
                f"background: {bg_color}; "
                f"border: 1px solid {border_color}; "
                "border-radius: 8px; padding: 10px; "
                "font-size: 13px; color: #FFFFFF;"
            )
            
            logger.info(f"Showed suggestion: {suggestion.text}")
        
        except Exception as e:
            logger.error(f"Error showing suggestion: {e}")
