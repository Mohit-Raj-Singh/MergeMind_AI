import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic.types import TextBlock

from ai_reviewer.models import ReviewResult, Severity
from ai_reviewer.providers.anthropic import AnthropicProvider
from ai_reviewer.providers.openai import OpenAIProvider

MOCK_RESULT = {
    "summary": {
        "overall": "Good PR overall.",
        "highlights": ["Clear variable names"],
        "issues": ["Missing error handling on line 10"],
        "security_flags": [],
    },
    "inline_comments": [
        {
            "path": "src/auth.py",
            "line": 10,
            "severity": "error",
            "title": "Missing error handling",
            "body": "This call can raise an exception. Wrap in try/except.",
        }
    ],
}


@pytest.mark.asyncio
async def test_anthropic_provider_parses_result():
    with patch("ai_reviewer.providers.anthropic.anthropic.AsyncAnthropic") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_block = MagicMock(spec=TextBlock, text=json.dumps(MOCK_RESULT))
        mock_client.messages.create = AsyncMock(
            return_value=MagicMock(content=[mock_block])
        )

        provider = AnthropicProvider(api_key="test-key", model="claude-sonnet-4-20250514")
        result = await provider.review("diff content", "standard", False)

        assert isinstance(result, ReviewResult)
        assert len(result.inline_comments) == 1
        assert result.inline_comments[0].severity == Severity.ERROR
        assert result.summary.overall == "Good PR overall."


@pytest.mark.asyncio
async def test_openai_provider_parses_result():
    with patch("ai_reviewer.providers.openai.AsyncOpenAI") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content=json.dumps(MOCK_RESULT)))]
            )
        )

        provider = OpenAIProvider(api_key="test-key", model="gpt-4o")
        result = await provider.review("diff content", "standard", False)

        assert isinstance(result, ReviewResult)
        assert result.inline_comments[0].path == "src/auth.py"
