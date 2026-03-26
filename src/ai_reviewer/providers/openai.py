import json

from openai import AsyncOpenAI

from ..models import ReviewResult
from .base import LLMProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def review(self, diff: str, review_level: str, security_only: bool) -> ReviewResult:
        response = await self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(diff, review_level, security_only)},
            ],
            max_tokens=4096,
        )
        raw = response.choices[0].message.content
        return ReviewResult.model_validate(json.loads(raw))
