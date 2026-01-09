"""
Async Ollama API client for LLM inference.
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any, AsyncIterator
import json

logger = logging.getLogger(__name__)


class OllamaClient:
    """Async client for Ollama API."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
        timeout: int = 5,
        max_retries: int = 2
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama API base URL.
            model: Model name to use.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries on failure.
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.available = False
        
        logger.info(f"Ollama Client initialized (model: {model}, url: {base_url})")
    
    async def check_health(self) -> bool:
        """
        Check if Ollama is running and model is available.
        
        Returns:
            True if Ollama is healthy, False otherwise.
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Check if Ollama is running
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        
                        # Check if our model is available
                        model_names = [m.get("name", "") for m in models]
                        self.available = any(self.model in name for name in model_names)
                        
                        if self.available:
                            logger.info(f"Ollama health check passed (model: {self.model})")
                        else:
                            logger.warning(f"Model {self.model} not found in Ollama")
                        
                        return self.available
                    else:
                        logger.warning(f"Ollama health check failed: HTTP {response.status}")
                        return False
        
        except asyncio.TimeoutError:
            logger.warning("Ollama health check timeout")
            return False
        except aiohttp.ClientError as e:
            logger.warning(f"Ollama health check failed: {e}")
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
        Generate text using Ollama.
        
        Args:
            prompt: Input prompt.
            temperature: Sampling temperature (0.0-1.0).
            max_tokens: Maximum tokens to generate.
            system_prompt: Optional system prompt.
        
        Returns:
            Generated text or None on failure.
        """
        # Build the full prompt with system prompt if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
            }
        }
        
        # Retry logic
        for attempt in range(self.max_retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/api/generate",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            generated_text = data.get("response", "").strip()
                            
                            logger.debug(f"Ollama generated: {generated_text}")
                            return generated_text
                        else:
                            error_text = await response.text()
                            logger.warning(f"Ollama generate failed: HTTP {response.status}, {error_text}")
                            
                            if attempt < self.max_retries:
                                await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                                continue
                            return None
            
            except asyncio.TimeoutError:
                logger.warning(f"Ollama generate timeout (attempt {attempt + 1}/{self.max_retries + 1})")
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                return None
            
            except aiohttp.ClientError as e:
                logger.error(f"Ollama client error: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                return None
            
            except Exception as e:
                logger.error(f"Unexpected error in generate: {e}")
                return None
        
        return None

    async def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 50,
        system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Generate text using Ollama with streaming support.

        Args:
            prompt: Input prompt.
            temperature: Sampling temperature (0.0-1.0).
            max_tokens: Maximum tokens to generate.
            system_prompt: Optional system prompt.

        Yields:
            Generated text chunks as they arrive.
        """
        # Build the full prompt with system prompt if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,  # Enable streaming
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout * 3)  # Longer timeout for streaming
                ) as response:
                    if response.status == 200:
                        # Read streaming response line by line
                        async for line in response.content:
                            if line:
                                try:
                                    chunk = json.loads(line.decode('utf-8'))
                                    text = chunk.get("response", "")
                                    if text:
                                        yield text

                                    # Check if this is the final chunk
                                    if chunk.get("done", False):
                                        break

                                except json.JSONDecodeError:
                                    logger.warning(f"Failed to decode streaming chunk: {line}")
                                    continue
                    else:
                        error_text = await response.text()
                        logger.warning(f"Ollama stream failed: HTTP {response.status}, {error_text}")
                        return

        except asyncio.TimeoutError:
            logger.warning("Ollama stream timeout")
            return
        except aiohttp.ClientError as e:
            logger.error(f"Ollama stream client error: {e}")
            return
        except Exception as e:
            logger.error(f"Unexpected error in stream: {e}")
            return

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
