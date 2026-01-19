"""
Configuration management for Mac Desktop Widget.
Provides type-safe configuration using Pydantic.
"""
from typing import Optional
from pydantic import BaseModel, Field, validator
import os


class MonitoringConfig(BaseModel):
    """Configuration for system monitoring."""
    
    update_interval_ms: int = Field(
        default=1000,
        description="Update frequency in milliseconds",
        ge=100,
        le=10000
    )
    
    cpu_threshold: float = Field(
        default=80.0,
        description="CPU usage threshold for anomaly detection (%)",
        ge=0.0,
        le=100.0
    )
    
    memory_threshold: float = Field(
        default=90.0,
        description="Memory usage threshold for anomaly detection (%)",
        ge=0.0,
        le=100.0
    )
    
    process_threshold: float = Field(
        default=50.0,
        description="Process resource threshold for anomaly detection (%)",
        ge=0.0,
        le=100.0
    )
    
    top_processes_count: int = Field(
        default=10,
        description="Number of top processes to display",
        ge=1,
        le=50
    )


class UIConfig(BaseModel):
    """Configuration for UI appearance and behavior."""
    
    window_width: int = Field(default=400, ge=200, le=1000)
    window_height: int = Field(default=600, ge=300, le=1200)
    window_x: Optional[int] = Field(default=None, description="Window X position")
    window_y: Optional[int] = Field(default=None, description="Window Y position")
    
    transparency: float = Field(
        default=0.9,
        description="Window transparency (0.0 = invisible, 1.0 = opaque)",
        ge=0.1,
        le=1.0
    )
    
    always_on_top: bool = Field(default=True)
    frameless: bool = Field(default=True)
    
    theme: str = Field(default="dark", pattern="^(dark|light)$")
    
    # Glassmorphism effect settings
    blur_radius: int = Field(default=20, ge=0, le=50)
    background_opacity: float = Field(default=0.3, ge=0.0, le=1.0)


class AIConfig(BaseModel):
    """Configuration for AI integration."""

    api_key: str = Field(
        default="",
        description="OpenAI API key (required for AI features)"
    )

    base_url: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API base URL (or compatible API endpoint)"
    )

    model_name: str = Field(
        default="gpt-3.5-turbo",
        description="OpenAI model to use (gpt-3.5-turbo recommended for speed)"
    )

    max_suggestion_length: int = Field(
        default=30,
        description="Maximum characters for AI suggestions",
        ge=10,
        le=100
    )

    suggestion_language: str = Field(
        default="zh_TW",
        description="Language for suggestions (zh_TW = Traditional Chinese)"
    )

    suggestion_cache_duration_seconds: int = Field(
        default=60,
        description="Cache duration to avoid duplicate suggestions",
        ge=10,
        le=3600
    )

    request_timeout_seconds: int = Field(
        default=5,
        description="Timeout for AI requests",
        ge=1,
        le=30
    )

    enable_ai: bool = Field(
        default=True,
        description="Enable/disable AI suggestions"
    )


class PerformanceConfig(BaseModel):
    """Performance limits and optimization settings."""
    
    max_cpu_overhead_percent: float = Field(
        default=2.0,
        description="Maximum CPU overhead allowed for the app itself",
        ge=0.5,
        le=10.0
    )
    
    max_memory_mb: int = Field(
        default=100,
        description="Maximum memory footprint in MB",
        ge=50,
        le=500
    )
    
    thread_pool_size: int = Field(
        default=3,
        description="Number of worker threads",
        ge=1,
        le=10
    )


class AppConfig(BaseModel):
    """Main application configuration container."""
    
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    
    # Debug settings
    debug_mode: bool = Field(default=False)
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    
    @classmethod
    def load_from_env(cls) -> "AppConfig":
        """Load configuration from environment variables."""
        config = cls()

        # Override with environment variables if present
        if os.getenv("UPDATE_INTERVAL_MS"):
            config.monitoring.update_interval_ms = int(os.getenv("UPDATE_INTERVAL_MS"))

        if os.getenv("OPENAI_API_KEY"):
            config.ai.api_key = os.getenv("OPENAI_API_KEY")

        if os.getenv("OPENAI_BASE_URL"):
            config.ai.base_url = os.getenv("OPENAI_BASE_URL")

        if os.getenv("OPENAI_MODEL"):
            config.ai.model_name = os.getenv("OPENAI_MODEL")

        if os.getenv("DEBUG"):
            config.debug_mode = os.getenv("DEBUG").lower() in ("true", "1", "yes")

        if os.getenv("LOG_LEVEL"):
            config.log_level = os.getenv("LOG_LEVEL").upper()

        return config
    
    def save_to_file(self, filepath: str) -> None:
        """Save configuration to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.model_dump_json(indent=2))
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "AppConfig":
        """Load configuration from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = f.read()
        return cls.model_validate_json(data)


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig.load_from_env()
    return _config


def set_config(config: AppConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
