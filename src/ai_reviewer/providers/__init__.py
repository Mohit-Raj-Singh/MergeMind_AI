from ..config import Provider
from .anthropic import AnthropicProvider
from .base import LLMProvider
from .gemini import GeminiProvider
from .openai import OpenAIProvider


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
