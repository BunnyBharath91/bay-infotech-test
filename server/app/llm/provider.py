"""
LLM provider abstraction layer.
Provides provider-agnostic interface for LLM interactions.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, List
from functools import lru_cache

from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[dict]] = None,
        temperature: float = 0.0
    ) -> str:
        """
        Generate response from LLM.
        
        Args:
            system_prompt: System prompt with instructions and KB context
            user_message: User's message
            conversation_history: Previous messages in conversation
            temperature: Temperature for generation (0.0 for determinism)
        
        Returns:
            Generated response text
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name
        """
        self.api_key = api_key
        self.model = model
        
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
            logger.info(f"OpenAI provider initialized with model: {model}")
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[dict]] = None,
        temperature: float = 0.0
    ) -> str:
        """Generate response using OpenAI API."""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class AnthropicProvider(LLMProvider):
    """Anthropic (Claude) LLM provider."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            model: Model name
        """
        self.api_key = api_key
        self.model = model
        
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=api_key)
            logger.info(f"Anthropic provider initialized with model: {model}")
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[dict]] = None,
        temperature: float = 0.0
    ) -> str:
        """Generate response using Anthropic API."""
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


class GoogleAIProvider(LLMProvider):
    """Google AI Studio (Gemini) LLM provider."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        """
        Initialize Google AI Studio provider.
        
        Args:
            api_key: Google AI Studio API key
            model: Model name (gemini-2.5-flash, gemini-2.5-pro, etc.)
        """
        self.api_key = api_key
        self.model = model
        
        try:
            from google import genai
            self.client = genai.Client(api_key=api_key)
            # Add models/ prefix if not present
            self.model_name = f"models/{model}" if not model.startswith("models/") else model
            logger.info(f"Google AI Studio provider initialized with model: {self.model_name}")
        except ImportError:
            raise ImportError("google-genai not installed. Run: pip install google-genai")
    
    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[dict]] = None,
        temperature: float = 0.0
    ) -> str:
        """Generate response using Google AI Studio API."""
        # Combine system prompt with user message for Gemini
        full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": 1000,
                }
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Google AI Studio error: {e}")
            raise


class MockProvider(LLMProvider):
    """Mock LLM provider for testing."""
    
    def __init__(self):
        """Initialize mock provider."""
        logger.info("Mock LLM provider initialized")
    
    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[dict]] = None,
        temperature: float = 0.0
    ) -> str:
        """Generate mock response."""
        return (
            "Based on the knowledge base, I can help you with that issue. "
            "Please follow the documented troubleshooting steps."
        )


@lru_cache()
def get_llm_provider() -> LLMProvider:
    """
    Get LLM provider based on configuration.
    
    Returns:
        LLMProvider instance
    """
    settings = get_settings()
    provider_name = settings.LLM_PROVIDER.lower()
    
    if provider_name == "openai":
        if not settings.LLM_API_KEY:
            raise ValueError("LLM_API_KEY not set for OpenAI provider")
        model = settings.LLM_MODEL or "gpt-4"
        return OpenAIProvider(api_key=settings.LLM_API_KEY, model=model)
    
    elif provider_name == "anthropic":
        if not settings.LLM_API_KEY:
            raise ValueError("LLM_API_KEY not set for Anthropic provider")
        model = settings.LLM_MODEL or "claude-3-sonnet-20240229"
        return AnthropicProvider(api_key=settings.LLM_API_KEY, model=model)
    
    elif provider_name == "gemini" or provider_name == "google":
        if not settings.LLM_API_KEY:
            raise ValueError("LLM_API_KEY not set for Google AI Studio provider")
        model = settings.LLM_MODEL or "gemini-1.5-flash"
        return GoogleAIProvider(api_key=settings.LLM_API_KEY, model=model)
    
    elif provider_name == "mock":
        return MockProvider()
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
