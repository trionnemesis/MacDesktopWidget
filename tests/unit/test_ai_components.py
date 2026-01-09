"""
Unit tests for AI components (Prompts, LangChain Agent).
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.python.ai.prompts.zh_tw_templates import (
    get_anomaly_type_name,
    format_anomaly_details,
    build_prompt_context,
    FALLBACK_SUGGESTIONS
)
from src.python.ai.langchain_agent import LangChainAgent
from src.python.monitoring.anomaly_detector import AnomalyType, AnomalySeverity, AnomalyEvent
from tests.fixtures.mock_data import create_mock_system_data


class TestPromptTemplates:
    """Test Traditional Chinese prompt templates."""

    def test_get_anomaly_type_name_cpu(self):
        """Test getting Chinese name for CPU anomaly."""
        name = get_anomaly_type_name("cpu")
        assert "CPU" in name
        assert "使用率" in name

    def test_get_anomaly_type_name_network(self):
        """Test getting Chinese name for network anomaly."""
        name = get_anomaly_type_name("network_io")
        assert "網路" in name

    def test_get_anomaly_type_name_battery_low(self):
        """Test getting Chinese name for battery low anomaly."""
        name = get_anomaly_type_name("battery_low")
        assert "電池" in name
        assert "電量" in name

    def test_get_anomaly_type_name_temperature(self):
        """Test getting Chinese name for temperature anomaly."""
        name = get_anomaly_type_name("high_temperature")
        assert "溫度" in name

    def test_get_anomaly_type_name_unknown(self):
        """Test getting name for unknown anomaly type."""
        name = get_anomaly_type_name("unknown_type")
        assert "系統" in name or "異常" in name

    def test_format_anomaly_details_cpu(self):
        """Test formatting CPU anomaly details."""
        details = format_anomaly_details(
            "cpu",
            {"cpu_percent": 92.5},
            process_name="Chrome"
        )
        assert "CPU" in details
        assert "92.5" in details or "92" in details
        assert "Chrome" in details

    def test_format_anomaly_details_network(self):
        """Test formatting network anomaly details."""
        details = format_anomaly_details(
            "network_io",
            {"total_mb_per_sec": 85.5, "upload_mb_per_sec": 40.0, "download_mb_per_sec": 45.5},
            process_name="Dropbox"
        )
        assert "網路" in details
        assert "Dropbox" in details

    def test_format_anomaly_details_battery_low(self):
        """Test formatting battery low anomaly details."""
        details = format_anomaly_details(
            "battery_low",
            {"battery_percent": 15.0, "time_remaining_hours": 1.5}
        )
        assert "電池" in details
        assert "15" in details

    def test_format_anomaly_details_temperature(self):
        """Test formatting temperature anomaly details."""
        details = format_anomaly_details(
            "high_temperature",
            {"max_temp": 88.0, "cpu_temp": 88.0}
        )
        assert "溫度" in details
        assert "88" in details

    def test_build_prompt_context(self):
        """Test building prompt context from system data."""
        # Create mock anomaly event
        anomaly_event = Mock()
        anomaly_event.type.value = "cpu"
        anomaly_event.metrics = {"cpu_percent": 92.0}
        anomaly_event.related_process = Mock()
        anomaly_event.related_process.name = "Chrome"
        anomaly_event.related_process.cpu_percent = 60.0
        anomaly_event.related_process.memory_percent = 25.0

        system_data = create_mock_system_data(cpu_percent=92.0, memory_percent=70.0)

        context = build_prompt_context(anomaly_event, system_data)

        assert context is not None
        assert "cpu_percent" in context
        assert context["cpu_percent"] == 92.0
        assert "top_process_name" in context
        assert context["top_process_name"] == "Chrome"

    def test_fallback_suggestions_exist(self):
        """Test that fallback suggestions exist for all anomaly types."""
        required_types = [
            "cpu", "memory", "process_cpu", "process_memory",
            "disk_io", "network_io", "battery_low", "battery_health", "high_temperature"
        ]

        for anomaly_type in required_types:
            assert anomaly_type in FALLBACK_SUGGESTIONS
            assert len(FALLBACK_SUGGESTIONS[anomaly_type]) > 0


class TestLangChainAgent:
    """Test LangChain agent functionality."""

    def test_langchain_agent_initialization(self):
        """Test LangChain agent can be initialized."""
        mock_ollama = Mock()
        agent = LangChainAgent(mock_ollama, max_suggestion_length=30)

        assert agent is not None
        assert agent.max_length == 30

    def test_validate_suggestion_valid(self):
        """Test validating a valid Traditional Chinese suggestion."""
        mock_ollama = Mock()
        agent = LangChainAgent(mock_ollama, max_suggestion_length=30)

        suggestion = "關閉 Chrome 分頁以降低負載"
        validated = agent._validate_suggestion(suggestion)

        assert validated is not None
        assert len(validated) <= 30

    def test_validate_suggestion_with_prefix(self):
        """Test validating suggestion with prefix that should be removed."""
        mock_ollama = Mock()
        agent = LangChainAgent(mock_ollama, max_suggestion_length=30)

        suggestion = "建議：關閉未使用的應用程式"
        validated = agent._validate_suggestion(suggestion)

        assert validated is not None
        assert not validated.startswith("建議：")
        assert "關閉" in validated

    def test_validate_suggestion_too_long(self):
        """Test validating suggestion that is too long."""
        mock_ollama = Mock()
        agent = LangChainAgent(mock_ollama, max_suggestion_length=30)

        long_suggestion = "這是一個非常非常非常非常非常非常非常非常非常長的建議內容超過三十個字"
        validated = agent._validate_suggestion(long_suggestion)

        assert validated is not None
        assert len(validated) <= 30
        assert validated.endswith("...")

    def test_validate_suggestion_empty(self):
        """Test validating empty suggestion."""
        mock_ollama = Mock()
        agent = LangChainAgent(mock_ollama, max_suggestion_length=30)

        validated = agent._validate_suggestion("")
        assert validated is None

    def test_validate_suggestion_not_chinese(self):
        """Test validating suggestion without Chinese characters."""
        mock_ollama = Mock()
        agent = LangChainAgent(mock_ollama, max_suggestion_length=30)

        # Pure English should fail validation
        suggestion = "Close Chrome tabs to reduce load"
        validated = agent._validate_suggestion(suggestion)

        assert validated is None

    def test_is_traditional_chinese_valid(self):
        """Test detecting valid Traditional Chinese text."""
        mock_ollama = Mock()
        agent = LangChainAgent(mock_ollama)

        text = "關閉 Chrome 分頁"
        assert agent._is_traditional_chinese(text) is True

    def test_is_traditional_chinese_with_mixed_content(self):
        """Test detecting Chinese text with mixed English/numbers."""
        mock_ollama = Mock()
        agent = LangChainAgent(mock_ollama)

        # Mixed content should still pass if >40% Chinese
        text = "CPU 使用率 92%"
        assert agent._is_traditional_chinese(text) is True

    def test_is_traditional_chinese_invalid(self):
        """Test detecting non-Chinese text."""
        mock_ollama = Mock()
        agent = LangChainAgent(mock_ollama)

        text = "Close Chrome tabs"
        assert agent._is_traditional_chinese(text) is False

    def test_get_fallback_suggestion(self):
        """Test getting fallback suggestion."""
        mock_ollama = Mock()
        agent = LangChainAgent(mock_ollama)

        suggestion = agent._get_fallback_suggestion("cpu")
        assert suggestion is not None
        assert len(suggestion) > 0
        assert "CPU" in suggestion or "cpu" in suggestion.lower()

    @pytest.mark.asyncio
    async def test_generate_suggestion_with_fallback(self):
        """Test generating suggestion falls back on error."""
        mock_ollama = AsyncMock()
        mock_ollama.generate_with_context = AsyncMock(return_value=None)

        agent = LangChainAgent(mock_ollama)

        # Create mock anomaly event
        anomaly_event = Mock()
        anomaly_event.type.value = "cpu"
        anomaly_event.metrics = {"cpu_percent": 92.0}
        anomaly_event.related_process = None

        system_data = create_mock_system_data(cpu_percent=92.0)

        suggestion = await agent.generate_suggestion(anomaly_event, system_data)

        # Should return fallback suggestion
        assert suggestion is not None
        assert len(suggestion) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
