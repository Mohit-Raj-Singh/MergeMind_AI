# Contributing to AI Code Reviewer

Thank you for your interest in contributing! Here's everything you need to get started.

## Ways to contribute

- **Add a new LLM provider** — the most impactful contribution (~30 lines of code)
- **Add platform support** — GitLab CI, Bitbucket Pipelines
- **Bug fixes** — open an issue first so we can discuss the fix
- **Documentation** — improving the README, adding examples

## Development setup

```bash
git clone https://github.com/Mohit-Raj-Singh/MergeMind_AI
cd MergeMind_AI
pip install -e ".[dev]"
pytest
```

## Adding a new LLM provider (step by step)

**1. Create the provider file**

```python
# src/ai_reviewer/providers/your_provider.py
from ..models import ReviewResult
from .base import LLMProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt
import json


class YourProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        # initialize your SDK client here
        self.model = model

    async def review(self, diff: str, review_level: str, security_only: bool) -> ReviewResult:
        # call your LLM API here
        raw_json = ...  # get JSON string from LLM
        return ReviewResult.model_validate(json.loads(raw_json))
```

**2. Register it in the factory**

```python
# src/ai_reviewer/providers/__init__.py
from .your_provider import YourProvider

def get_provider(provider, api_key, model):
    match provider:
        ...
        case Provider.YOUR_PROVIDER:
            return YourProvider(api_key=api_key, model=model)
```

**3. Add the enum value and default model**

```python
# src/ai_reviewer/config.py
class Provider(StrEnum):
    ...
    YOUR_PROVIDER = "your_provider"

DEFAULT_MODELS = {
    ...
    Provider.YOUR_PROVIDER: "your-default-model-name",
}
```

**4. Add the dependency**

```toml
# pyproject.toml
dependencies = [
    ...
    "your-sdk>=1.0.0",
]
```

**5. Update `action.yml` and `README.md`**

Add the new provider name to the `provider` input description in `action.yml` and add a row to the providers table in `README.md`.

**6. Add a test**

Follow the pattern in `tests/test_providers.py` — mock the SDK client and assert the result parses correctly.

## Code style

We use `ruff` for linting and formatting:

```bash
ruff check .
ruff format .
```

## Running tests

```bash
pytest                    # all tests
pytest -v                 # verbose
pytest tests/test_providers.py  # specific file
```

## Opening a PR

- Keep PRs focused — one feature or fix per PR
- Include a test for any new code
- Update the README if you're adding a feature users need to know about
- Fill out the PR template

## Reporting bugs

Open an issue with:
- What you expected to happen
- What actually happened
- Your workflow YAML (redact API keys)
- The action logs (from the Actions tab)
