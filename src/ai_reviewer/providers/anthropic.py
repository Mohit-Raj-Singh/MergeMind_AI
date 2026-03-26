import json

import anthropic
from anthropic.types import TextBlock

from ..models import ReviewResult
from .base import LLMProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def review(self, diff: str, review_level: str, security_only: bool) -> ReviewResult:
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": build_user_prompt(diff, review_level, security_only)}
            ],
        )
        raw = next(block.text for block in message.content if isinstance(block, TextBlock))
        return ReviewResult.model_validate(json.loads(raw))
