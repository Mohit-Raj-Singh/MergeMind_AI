from enum import StrEnum
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class Provider(StrEnum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"


class ReviewLevel(StrEnum):
    QUICK = "quick"
    STANDARD = "standard"
    THOROUGH = "thorough"


def _load_default_models() -> dict[Provider, str]:
    models_file = Path(__file__).parent / "models.yml"
    with models_file.open() as f:
        data = yaml.safe_load(f)
    return {Provider(k): v for k, v in data["defaults"].items()}


DEFAULT_MODELS: dict[Provider, str] = _load_default_models()


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_ignore_empty=True)

    # Required
    provider: Provider
    api_key: str

    # GitHub context (injected by Actions runtime)
    github_token: str
    github_repository: str
    github_event_path: str

    # Optional tuning
    model: str | None = None
    review_level: ReviewLevel = ReviewLevel.STANDARD
    ignore_paths: str = ""
    post_summary: bool = True
    post_inline: bool = True
    security_only: bool = False

    @property
    def resolved_model(self) -> str:
        return self.model or DEFAULT_MODELS[self.provider]

    @property
    def ignore_patterns(self) -> list[str]:
        if not self.ignore_paths:
            return []
        return [p.strip() for p in self.ignore_paths.split(",") if p.strip()]
