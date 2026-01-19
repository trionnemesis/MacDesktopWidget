"""
Async OpenAI API client for LLM inference.
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Async client for OpenAI API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        timeout: int = 5,
        max_retries: int = 2,
        base_url: str = "https://api.openai.com/v1"
    ):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key.
            model: Model name to use (e.g., "gpt-3.5-turbo", "gpt-4").
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries on failure.
            base_url: OpenAI API base URL (can be changed for compatible APIs).
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.available = False

        if not api_key:
            logger.error("OpenAI API key is required")
        else:
            logger.info(f"OpenAI Client initialized (model: {model})")

    async def check_health(self) -> bool:
        """
        Check if OpenAI API is accessible.

        Returns:
            True if API is healthy, False otherwise.
        """
        if not self.api_key:
            logger.warning("No API key provided")
            return False

        try:
            async with aiohttp.ClientSession() as session:
                # Try a simple API call to check health
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 5
                }

                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        self.available = True
                        logger.info(f"OpenAI health check passed (model: {self.model})")
                        return True
                    else:
                        error_text = await response.text()
                        logger.warning(f"OpenAI health check failed: HTTP {response.status}, {error_text}")
                        return False

        except asyncio.TimeoutError:
            logger.warning("OpenAI health check timeout")
            return False
        except aiohttp.ClientError as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in health check: {e}")
            return False

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 50,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate text using OpenAI API.

        Args:
            prompt: Input prompt.
            temperature: Sampling temperature (0.0-2.0).
            max_tokens: Maximum tokens to generate.
            system_prompt: Optional system prompt.

        Returns:
            Generated text or None on failure.
        """
        if not self.api_key:
            logger.error("No API key available")
            return None

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.9
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Retry logic
        for attempt in range(self.max_retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            generated_text = data["choices"][0]["message"]["content"].strip()

                            logger.debug(f"OpenAI generated: {generated_text}")
                            return generated_text
                        else:
                            error_text = await response.text()
                            logger.warning(f"OpenAI generate failed: HTTP {response.status}, {error_text}")

                            if attempt < self.max_retries:
                                await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                                continue
                            return None

            except asyncio.TimeoutError:
                logger.warning(f"OpenAI generate timeout (attempt {attempt + 1}/{self.max_retries + 1})")
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                return None

            except aiohttp.ClientError as e:
                logger.error(f"OpenAI client error: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                return None

            except Exception as e:
                logger.error(f"Unexpected error in generate: {e}")
                return None

        return None

    async def generate_with_context(
        self,
        context_template: str,
        context_vars: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 50
    ) -> Optional[str]:
        """
        Generate text with a context template.

        Args:
            context_template: Template string with placeholders.
            context_vars: Dictionary of variables to fill template.
            system_prompt: Optional system prompt.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.

        Returns:
            Generated text or None on failure.
        """
        try:
            # Fill in the template
            prompt = context_template.format(**context_vars)

            # Generate
            return await self.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt
            )

        except KeyError as e:
            logger.error(f"Missing context variable: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in generate_with_context: {e}")
            return None
