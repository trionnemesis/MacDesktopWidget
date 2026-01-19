"""
AI suggestion engine coordinating anomaly detection and AI generation.
"""
from PyQt6.QtCore import QThread, pyqtSignal
import asyncio
import time
from typing import Optional, Dict
from dataclasses import dataclass
import logging
import qasync

from .openai_client import OpenAIClient
from .langchain_agent import LangChainAgent

logger = logging.getLogger(__name__)


@dataclass
class Suggestion:
    """AI suggestion with metadata."""
    text: str
    anomaly_type: str
    timestamp: float
    severity: str


class SuggestionEngine(QThread):
    """
    Background thread for generating AI suggestions.
    Handles queuing, caching, and rate limiting.
    """
    
    # Signal emitted when new suggestion is ready
    suggestion_ready = pyqtSignal(Suggestion)
    
    # Signal for errors
    error_occurred = pyqtSignal(str)
    
    # Signal for AI status changes
    ai_status_changed = pyqtSignal(bool)  # True if available, False if not
    
    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://api.openai.com/v1",
        model_name: str = "gpt-3.5-turbo",
        cache_duration: int = 60,
        rate_limit_seconds: int = 10,
        max_suggestion_length: int = 30
    ):
        """
        Initialize suggestion engine.

        Args:
            api_key: OpenAI API key.
            base_url: OpenAI API base URL.
            model_name: Model to use.
            cache_duration: Cache duration in seconds.
            rate_limit_seconds: Minimum seconds between requests.
            max_suggestion_length: Maximum suggestion length.
        """
        super().__init__()

        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.cache_duration = cache_duration
        self.rate_limit = rate_limit_seconds
        self.max_length = max_suggestion_length

        # Components (initialized in run())
        self.ai_client: Optional[OpenAIClient] = None
        self.agent: Optional[LangChainAgent] = None

        # State
        self.running = False
        self.ai_available = False
        self.last_request_time = 0.0

        # Caching
        self.suggestion_cache: Dict[str, Suggestion] = {}

        # Queue for anomaly events
        self.anomaly_queue = asyncio.Queue()

        # Current system data (updated from monitoring)
        self.current_system_data = None

        logger.info("Suggestion Engine initialized")
    
    def run(self) -> None:
        """Main thread loop (async)."""
        self.running = True
        
        # Create async event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._async_run())
        except Exception as e:
            logger.error(f"Error in suggestion engine loop: {e}", exc_info=True)
        finally:
            loop.close()
    
    async def _async_run(self) -> None:
        """Async main loop."""
        # Initialize OpenAI client and agent
        self.ai_client = OpenAIClient(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model_name,
            timeout=5,
            max_retries=2
        )

        self.agent = LangChainAgent(
            ai_client=self.ai_client,
            max_suggestion_length=self.max_length
        )

        # Check OpenAI health
        self.ai_available = await self.ai_client.check_health()
        self.ai_status_changed.emit(self.ai_available)

        if not self.ai_available:
            logger.warning("OpenAI API not available - using fallback suggestions only")

        # Main processing loop
        while self.running:
            try:
                # Wait for anomaly event (with timeout to allow checking running flag)
                try:
                    anomaly_event = await asyncio.wait_for(
                        self.anomaly_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Process the anomaly
                await self._process_anomaly(anomaly_event)

            except Exception as e:
                logger.error(f"Error processing anomaly: {e}", exc_info=True)
                self.error_occurred.emit(str(e))
    
    async def _process_anomaly(self, anomaly_event) -> None:
        """
        Process an anomaly event and generate suggestion.

        Args:
            anomaly_event: AnomalyEvent to process.
        """
        now = time.time()

        # Edge filtering: Skip anomalies that don't need AI suggestions
        if not self._should_generate_suggestion(anomaly_event):
            logger.debug(f"Edge filter: Skipping AI suggestion for {anomaly_event.type}")
            return

        # Check cache first
        cache_key = anomaly_event.get_signature()
        if cache_key in self.suggestion_cache:
            cached = self.suggestion_cache[cache_key]
            if now - cached.timestamp < self.cache_duration:
                logger.debug(f"Using cached suggestion for {anomaly_event.type}")
                self.suggestion_ready.emit(cached)
                return

        # Check rate limit
        if now - self.last_request_time < self.rate_limit:
            logger.debug(f"Rate limit - skipping suggestion for {anomaly_event.type}")
            return

        # Generate suggestion
        if self.current_system_data is None:
            logger.warning("No system data available for suggestion context")
            return

        try:
            suggestion_text = await self.agent.generate_suggestion(
                anomaly_event,
                self.current_system_data
            )

            # Create suggestion object
            suggestion = Suggestion(
                text=suggestion_text,
                anomaly_type=anomaly_event.type.value,
                timestamp=now,
                severity=anomaly_event.severity.value
            )

            # Cache it
            self.suggestion_cache[cache_key] = suggestion

            # Update rate limit
            self.last_request_time = now

            # Emit signal
            self.suggestion_ready.emit(suggestion)

            logger.info(f"Generated and emitted suggestion: {suggestion_text}")

        except Exception as e:
            logger.error(f"Error generating suggestion: {e}", exc_info=True)
            self.error_occurred.emit(str(e))

    def _should_generate_suggestion(self, anomaly_event) -> bool:
        """
        Edge filtering logic: Determine if an anomaly warrants AI suggestion.

        Args:
            anomaly_event: AnomalyEvent to evaluate.

        Returns:
            True if suggestion should be generated, False otherwise.
        """
        from ..monitoring.anomaly_detector import AnomalySeverity, AnomalyType

        # Always generate for CRITICAL severity
        if anomaly_event.severity == AnomalySeverity.CRITICAL:
            return True

        # Skip INFO level anomalies for disk/network I/O unless very high
        if anomaly_event.severity == AnomalySeverity.INFO:
            if anomaly_event.type == AnomalyType.DISK_IO:
                # Only generate if disk I/O > 500 MB/s
                if anomaly_event.metrics.get("max_io_mb_per_sec", 0) < 500:
                    return False
            elif anomaly_event.type == AnomalyType.NETWORK_IO:
                # Only generate if network I/O > 100 MB/s
                if anomaly_event.metrics.get("total_mb_per_sec", 0) < 100:
                    return False

        # For WARNING level, apply additional filters
        if anomaly_event.severity == AnomalySeverity.WARNING:
            # Skip short-duration anomalies (< 10 seconds)
            if anomaly_event.duration_seconds < 10:
                return False

            # For process anomalies, only generate if process is using > 75% resources
            if anomaly_event.type in [AnomalyType.PROCESS_CPU, AnomalyType.PROCESS_MEMORY]:
                primary_value = anomaly_event.metrics.get("primary_value", 0)
                if primary_value < 75:
                    return False

            # For battery health, only generate if health < 70%
            if anomaly_event.type == AnomalyType.BATTERY_HEALTH:
                health = anomaly_event.metrics.get("health_percent", 100)
                if health >= 70:
                    return False

        # For temperature, only generate if sustained for > 30 seconds
        if anomaly_event.type == AnomalyType.HIGH_TEMPERATURE:
            if anomaly_event.duration_seconds < 30:
                return False

        return True
    
    def handle_anomaly(self, anomaly_event) -> None:
        """
        Handle new anomaly event (called from main thread).
        
        Args:
            anomaly_event: AnomalyEvent to queue.
        """
        # Queue the anomaly for processing
        # Note: This is called from main thread, so we use thread-safe method
        asyncio.run_coroutine_threadsafe(
            self.anomaly_queue.put(anomaly_event),
            asyncio.get_event_loop()
        )
    
    def update_system_data(self, system_data) -> None:
        """
        Update current system data for context.
        
        Args:
            system_data: Latest SystemData.
        """
        self.current_system_data = system_data
    
    def stop(self) -> None:
        """Stop the suggestion engine."""
        logger.info("Stopping Suggestion Engine...")
        self.running = False
    
    def clear_cache(self) -> None:
        """Clear the suggestion cache."""
        self.suggestion_cache.clear()
        logger.info("Suggestion cache cleared")
