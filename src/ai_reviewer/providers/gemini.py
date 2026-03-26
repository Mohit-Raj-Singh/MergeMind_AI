import json

import google.generativeai as genai

from ..models import ReviewResult
from .base import LLMProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        genai.configure(api_key=api_key)  # type: ignore[attr-defined]
        self.model = genai.GenerativeModel(  # type: ignore[attr-defined]
            model_name=model,
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(  # type: ignore[attr-defined]
                response_mime_type="application/json",
                max_output_tokens=4096,
            ),
        )

    async def review(self, diff: str, review_level: str, security_only: bool) -> ReviewResult:
        response = await self.model.generate_content_async(
            build_user_prompt(diff, review_level, security_only)
        )
        return ReviewResult.model_validate(json.loads(response.text))
