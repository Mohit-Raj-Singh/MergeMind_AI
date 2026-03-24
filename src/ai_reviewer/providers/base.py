from abc import ABC, abstractmethod
from ..models import ReviewResult


class LLMProvider(ABC):
    """Abstract base — implement one method to add a new provider."""

    @abstractmethod
    async def review(self, diff: str, review_level: str, security_only: bool) -> ReviewResult:
        """Send diff to LLM, return structured review result."""
        ...
