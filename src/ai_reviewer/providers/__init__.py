from ..config import Provider
from .base import LLMProvider
from .anthropic import AnthropicProvider
from .openai import OpenAIProvider
from .gemini import GeminiProvider


def get_provider(provider: Provider, api_key: str, model: str) -> LLMProvider:
    match provider:
        case Provider.ANTHROPIC:
            return AnthropicProvider(api_key=api_key, model=model)
        case Provider.OPENAI:
            return OpenAIProvider(api_key=api_key, model=model)
        case Provider.GEMINI:
            return GeminiProvider(api_key=api_key, model=model)
        case _:
            raise ValueError(f"Unknown provider: {provider}")
