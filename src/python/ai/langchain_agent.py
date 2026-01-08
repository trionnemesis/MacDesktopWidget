"""
LangChain agent for system monitoring suggestions.
"""
import logging
import asyncio
from typing import Optional
import unicodedata

from .ollama_client import OllamaClient
from .prompts.zh_tw_templates import (
    SYSTEM_PROMPT,
    CONTEXT_TEMPLATE,
    FALLBACK_SUGGESTIONS,
    build_prompt_context
)

logger = logging.getLogger(__name__)


class LangChainAgent:
    """LangChain-based agent for generating system monitoring suggestions."""
    
    def __init__(
        self,
        ollama_client: OllamaClient,
        max_suggestion_length: int = 30
    ):
        """
        Initialize LangChain agent.
        
        Args:
            ollama_client: OllamaClient instance.
            max_suggestion_length: Maximum characters for suggestions.
        """
        self.ollama = ollama_client
        self.max_length = max_suggestion_length
        
        logger.info("LangChain Agent initialized")
    
    async def generate_suggestion(
        self,
        anomaly_event,
        system_data
    ) -> str:
        """
        Generate a Traditional Chinese suggestion for an anomaly.
        
        Args:
            anomaly_event: AnomalyEvent object.
            system_data: SystemData object.
        
        Returns:
            Traditional Chinese suggestion string.
        """
        try:
            # Build context from anomaly and system data
            context = build_prompt_context(anomaly_event, system_data)
            
            # Generate using Ollama
            response = await self.ollama.generate_with_context(
                context_template=CONTEXT_TEMPLATE,
                context_vars=context,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.7,
                max_tokens=50
            )
            
            if response:
                # Validate and clean response
                suggestion = self._validate_suggestion(response)
                
                if suggestion:
                    logger.info(f"Generated suggestion: {suggestion}")
                    return suggestion
            
            # Fallback if generation failed or invalid
            logger.warning("Using fallback suggestion")
            return self._get_fallback_suggestion(anomaly_event.type.value)
        
        except Exception as e:
            logger.error(f"Error generating suggestion: {e}")
            return self._get_fallback_suggestion(anomaly_event.type.value)
    
    def _validate_suggestion(self, suggestion: str) -> Optional[str]:
        """
        Validate and clean AI-generated suggestion.
        
        Args:
            suggestion: Raw suggestion text.
        
        Returns:
            Cleaned suggestion or None if invalid.
        """
        # Clean whitespace
        clean = suggestion.strip()
        
        # Remove common prefixes that AI might add
        prefixes_to_remove = ["建議：", "建議:", "回答：", "回答:", "答：", "答:"]
        for prefix in prefixes_to_remove:
            if clean.startswith(prefix):
                clean = clean[len(prefix):].strip()
        
        # Check length
        if len(clean) == 0:
            logger.warning("Empty suggestion after cleaning")
            return None
        
        if len(clean) > self.max_length:
            # Truncate at max length - 3 and add ellipsis
            clean = clean[:self.max_length - 3] + "..."
            logger.debug(f"Truncated suggestion to {self.max_length} chars")
        
        # Verify it contains Traditional Chinese
        if not self._is_traditional_chinese(clean):
            logger.warning(f"Suggestion doesn't appear to be Traditional Chinese: {clean}")
            return None
        
        return clean
    
    def _is_traditional_chinese(self, text: str) -> bool:
        """
        Check if text contains primarily Traditional Chinese characters.
        
        Args:
            text: Text to check.
        
        Returns:
            True if text is primarily Chinese characters.
        """
        if len(text) == 0:
            return False
        
        # Count CJK characters
        chinese_count = sum(
            1 for c in text
            if '\u4e00' <= c <= '\u9fff' or  # CJK Unified Ideographs
               '\u3400' <= c <= '\u4dbf' or  # CJK Extension A
               '\uf900' <= c <= '\ufaff'     # CJK Compatibility Ideographs
        )
        
        # Should be at least 40% Chinese characters
        # (allowing for numbers, punctuation, English process names)
        return chinese_count / len(text) >= 0.4
    
    def _get_fallback_suggestion(self, anomaly_type: str) -> str:
        """
        Get fallback suggestion when AI is unavailable.
        
        Args:
            anomaly_type: Type of anomaly.
        
        Returns:
            Fallback suggestion string.
        """
        return FALLBACK_SUGGESTIONS.get(anomaly_type, "系統資源使用異常")
