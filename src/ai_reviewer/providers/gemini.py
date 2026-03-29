import json

import google.genai as genai
from google.genai import types as genai_types

from ..models import ReviewResult
from .base import LLMProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.config = genai_types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            max_output_tokens=1024,
        )

    async def review(self, diff: str, review_level: str, security_only: bool) -> ReviewResult:
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=build_user_prompt(diff, review_level, security_only),
            config=self.config,
        )
        if response.text is None:
            raise ValueError("Gemini returned empty response")
        return ReviewResult.model_validate(json.loads(response.text))
